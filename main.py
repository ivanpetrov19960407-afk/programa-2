from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QApplication
from qasync import QEventLoop
from qfluentwidgets import FluentIcon as F
from qfluentwidgets import FluentWindow, NavigationItemPosition

from core.ai_engine import AiInferenceEngine
from core.security import SecurityService
from core.vpn_manager import VpnConfig, VpnManager
from ui.chat_widget import ChatWidget
from ui.settings_widget import SettingsWidget


def resource_path(relative_path: str) -> Path:
    """Возвращает путь к ресурсу с учетом PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / relative_path
    return Path(relative_path)


class MainWindow(FluentWindow):
    """Главное окно приложения."""

    def __init__(self, ai_engine: AiInferenceEngine, vpn_manager: VpnManager) -> None:
        super().__init__()
        self.setWindowTitle("Universal AI Assistant")
        self.resize(1100, 720)

        chat_widget = ChatWidget(ai_engine, self)
        settings_widget = SettingsWidget(vpn_manager, ai_engine, self)

        self.addSubInterface(chat_widget, F.CHAT, "Чат")
        self.addSubInterface(
            settings_widget, F.SETTING, "Настройки", NavigationItemPosition.BOTTOM
        )


def main() -> None:
    """Точка входа приложения."""
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    security_service = SecurityService()
    ai_engine = AiInferenceEngine(security_service)

    vpn_config = VpnConfig(
        binary_path=resource_path("wireproxy"),
        config_path=resource_path("config/wireguard.conf"),
    )
    vpn_manager = VpnManager(vpn_config)

    window = MainWindow(ai_engine, vpn_manager)
    window.show()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
