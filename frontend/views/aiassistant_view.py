#!/usr/bin/env python3
"""AI Assistant tab providing simple chat interface."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

try:
    from backend.services.api_client import AIAssistantAPIClient
except ImportError:  # pragma: no cover
    import os
    import sys

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)
    if GRANDPARENT_DIR not in sys.path:
        sys.path.insert(0, GRANDPARENT_DIR)
    from backend.services.api_client import AIAssistantAPIClient


class AIAssistantView(Gtk.Box):
    """Basic AI chat view backed by the ZeusNet API."""

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)

        self.api_client = AIAssistantAPIClient()

        self.chat_view = Gtk.TextView()
        self.chat_view.set_editable(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.chat_buffer = self.chat_view.get_buffer()

        input_box = Gtk.Box(spacing=6)
        self.entry = Gtk.Entry()
        send_btn = Gtk.Button(label="Send")
        send_btn.connect("clicked", self.on_send)
        input_box.append(self.entry)
        input_box.append(send_btn)

        self.append(self.chat_view)
        self.append(input_box)

    def _append_text(self, text: str) -> None:
        end = self.chat_buffer.get_end_iter()
        self.chat_buffer.insert(end, text)
        mark = self.chat_buffer.get_insert()
        self.chat_view.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)

    def on_send(self, _btn: Gtk.Button) -> None:
        prompt = self.entry.get_text()
        if not prompt:
            return
        self.entry.set_text("")
        self._append_text(f"You: {prompt}\n")

        def _on_success(data: dict) -> None:
            self._append_text(f"AI: {data.get('response', '')}\n")

        def _on_error(err: Exception) -> None:
            self._append_text(f"Error: {err}\n")

        self.api_client.ask_async(prompt, _on_success, _on_error)
