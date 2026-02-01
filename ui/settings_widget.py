from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from qfluentwidgets import SwitchButton

from core.ai_engine import AiInferenceEngine
from core.vpn_manager import VpnManager


class SettingsWidget(QWidget):
    """Виджет настроек VPN."""

    def __init__(
        self,
        vpn_manager: VpnManager,
        ai_engine: AiInferenceEngine,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._vpn_manager = vpn_manager
        self._ai_engine = ai_engine

        self._status_label = QLabel("VPN выключен", self)
        self._status_label.setStyleSheet("color: red;")

        self._vpn_switch = SwitchButton(self)
        self._vpn_switch.setText("Использовать VPN")
        self._vpn_switch.checkedChanged.connect(self._handle_vpn_toggle)

        layout = QVBoxLayout(self)
        layout.addWidget(self._vpn_switch)
        layout.addWidget(self._status_label)
        layout.addStretch(1)
        self.setLayout(layout)

        if self._vpn_manager.worker:
            self._vpn_manager.worker.vpn_status_signal.connect(self._update_status)

    def _handle_vpn_toggle(self, checked: bool) -> None:
        """Включает или выключает VPN."""
        self._ai_engine.use_vpn = checked
        if checked:
            self._vpn_manager.start_vpn()
            if self._vpn_manager.worker:
                self._vpn_manager.worker.vpn_status_signal.connect(self._update_status)
        else:
            self._vpn_manager.stop_vpn()
            self._update_status(False, "VPN выключен")

    def _update_status(self, is_connected: bool, message: str) -> None:
        """Обновляет статусную метку."""
        color = "green" if is_connected else "red"
        self._status_label.setStyleSheet(f"color: {color};")
        self._status_label.setText(message)
