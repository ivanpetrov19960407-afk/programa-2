from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal


@dataclass
class VpnConfig:
    \"\"\"Конфигурация запуска userspace VPN.\"\"\"

    binary_path: Path
    config_path: Path
    socks_host: str = \"127.0.0.1\"
    socks_port: int = 1080


class VpnWorker(QThread):
    \"\"\"Поток, который запускает VPN-процесс и отслеживает его статус.\"\"\"

    vpn_status_signal = pyqtSignal(bool, str)

    def __init__(self, config: VpnConfig) -> None:
        super().__init__()
        self._config = config
        self._process: Optional[subprocess.Popen[str]] = None
        self._stop_requested = False

    def run(self) -> None:
        \"\"\"Запускает процесс wireproxy/wireguard-go и следит за stdout.\"\"\"
        self._stop_requested = False
        command = [
            str(self._config.binary_path),
            \"--config\",
            str(self._config.config_path),
        ]
        creation_flags = 0
        if sys.platform == \"win32\":
            creation_flags = subprocess.CREATE_NO_WINDOW
        try:
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=creation_flags,
            )
        except FileNotFoundError:
            self.vpn_status_signal.emit(False, \"VPN бинарник не найден\")
            return
        except Exception as exc:
            self.vpn_status_signal.emit(False, f\"Ошибка запуска VPN: {exc}\")
            return

        if not self._process.stdout:
            self.vpn_status_signal.emit(False, \"Нет stdout у процесса VPN\")
            return

        for line in self._process.stdout:
            if self._stop_requested:
                break
            normalized = line.strip()
            if \"Serving SOCKS5\" in normalized or \"Ready\" in normalized:
                self.vpn_status_signal.emit(True, \"VPN подключен\")
            if normalized:
                self.vpn_status_signal.emit(True, normalized)

        self.vpn_status_signal.emit(False, \"VPN остановлен\")

    def stop(self) -> None:
        \"\"\"Останавливает VPN-процесс.\"\"\"
        self._stop_requested = True
        if self._process and self._process.poll() is None:
            self._process.terminate()


class VpnManager:
    \"\"\"Фасад для управления VPN воркером.\"\"\"

    def __init__(self, config: VpnConfig) -> None:
        self._config = config
        self._worker: Optional[VpnWorker] = None

    @property
    def worker(self) -> Optional[VpnWorker]:
        return self._worker

    def start_vpn(self) -> None:
        \"\"\"Запускает VPN-подключение.\"\"\"
        if self._worker and self._worker.isRunning():
            return
        self._worker = VpnWorker(self._config)
        self._worker.start()

    def stop_vpn(self) -> None:
        \"\"\"Останавливает VPN-подключение.\"\"\"
        if not self._worker:
            return
        self._worker.stop()
        self._worker.wait()
