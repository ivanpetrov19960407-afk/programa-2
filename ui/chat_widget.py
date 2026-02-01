from __future__ import annotations

from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qasync import asyncSlot
from qfluentwidgets import ComboBox, PrimaryPushButton, TextEdit

from core.ai_engine import AiInferenceEngine


class ChatWidget(QWidget):
    """Виджет чата с поддержкой потоковой генерации."""

    def __init__(self, ai_engine: AiInferenceEngine, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ai_engine = ai_engine
        self._messages: List[dict] = []

        self._chat_history = TextEdit(self)
        self._chat_history.setReadOnly(True)

        self._input_box = TextEdit(self)
        self._input_box.setPlaceholderText("Введите сообщение...")

        self._model_selector = ComboBox(self)
        self._model_selector.addItems(["gpt-4o-mini", "claude-3-haiku"])

        self._send_button = PrimaryPushButton("Отправить", self)
        self._send_button.clicked.connect(self.send_message)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Модель:", self))
        controls_layout.addWidget(self._model_selector)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self._send_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._chat_history)
        layout.addWidget(self._input_box)
        layout.addLayout(controls_layout)
        self.setLayout(layout)

    @asyncSlot()
    async def send_message(self) -> None:
        """Отправляет сообщение и обновляет UI по мере ответа."""
        user_text = self._input_box.toPlainText().strip()
        if not user_text:
            return

        self._messages.append({"role": "user", "content": user_text})
        self._chat_history.append(f"Вы: {user_text}\nАссистент: ")
        self._input_box.clear()

        model = self._model_selector.currentText()
        assistant_reply = []
        async for token in self._ai_engine.generate_response_stream(model, self._messages):
            assistant_reply.append(token)
            cursor = self._chat_history.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(token)
            self._chat_history.setTextCursor(cursor)
            self._chat_history.ensureCursorVisible()
        self._chat_history.append("")

        self._messages.append({"role": "assistant", "content": "".join(assistant_reply)})
