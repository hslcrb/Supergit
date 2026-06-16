"""Supergit 터미널 탭"""

import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent, QTextCursor


class CommandRunner(QThread):
    done = pyqtSignal(str, bool)

    def __init__(self, command: str, cwd: str):
        super().__init__()
        self._cmd = command
        self._cwd = cwd

    def run(self):
        try:
            result = subprocess.run(
                self._cmd, cwd=self._cwd, shell=True,
                capture_output=True, text=True,
                timeout=30, encoding="utf-8", errors="replace"
            )
            output = (result.stdout or "") + (result.stderr or "")
            self.done.emit(output.strip() or "(출력 없음)", result.returncode == 0)
        except subprocess.TimeoutExpired:
            self.done.emit("오류: 타임아웃 (30초)", False)
        except Exception as e:
            self.done.emit(f"오류: {e}", False)


class TerminalInput(QLineEdit):
    """히스토리 탐색 지원 입력창"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = []
        self._history_idx = -1

    def add_history(self, cmd: str):
        if cmd and (not self._history or self._history[-1] != cmd):
            self._history.append(cmd)
        self._history_idx = -1

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key.Key_Up:
            if self._history and self._history_idx < len(self._history) - 1:
                self._history_idx += 1
                self.setText(self._history[-(self._history_idx + 1)])
        elif e.key() == Qt.Key.Key_Down:
            if self._history_idx > 0:
                self._history_idx -= 1
                self.setText(self._history[-(self._history_idx + 1)])
            elif self._history_idx == 0:
                self._history_idx = -1
                self.clear()
        else:
            super().keyPressEvent(e)


class TerminalPanel(QWidget):
    def __init__(self, git_ops, i18n, theme, parent=None):
        super().__init__(parent)
        self.git = git_ops
        self.t = i18n
        self.theme = theme
        self._workers = []
        self._setup_ui()
        self._print_welcome()

    def _setup_ui(self):
        c = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # 헤더
        hdr = QHBoxLayout()
        title = QLabel(self.t("tab_terminal"))
        title.setStyleSheet(f"color:{c['fg']}; font-size:13px; font-weight:bold;")
        hdr.addWidget(title)
        hdr.addStretch()

        if self.git:
            cwd_label = QLabel(self.git.repo_path)
            cwd_label.setStyleSheet(f"color:{c['fg3']}; font-size:11px;")
            hdr.addWidget(cwd_label)

        btn_clear = QPushButton(self.t("terminal_clear"))
        btn_clear.setFixedHeight(26)
        btn_clear.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{c['fg3']}; border:1px solid {c['border']};"
            f"border-radius:4px; padding:2px 10px; font-size:11px; }}"
            f"QPushButton:hover {{ background:{c['bg3']}; }}"
        )
        btn_clear.clicked.connect(self._clear)
        hdr.addWidget(btn_clear)
        layout.addLayout(hdr)

        # 출력창
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background: {c['bg2']}; color: {c['green']}; border: 1px solid {c['border']};
                border-radius: 6px; font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px; padding: 8px;
            }}
            """
        )
        layout.addWidget(self.output, stretch=1)

        # 입력창
        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.prompt_lbl = QLabel("$")
        self.prompt_lbl.setStyleSheet(
            f"color:{c['accent']}; font-family:'Consolas',monospace; font-size:13px; font-weight:bold;"
        )
        input_row.addWidget(self.prompt_lbl)

        self.cmd_input = TerminalInput()
        self.cmd_input.setPlaceholderText(self.t("terminal_prompt"))
        self.cmd_input.setStyleSheet(
            f"""
            QLineEdit {{
                background: {c['bg2']}; color: {c['fg']}; border: 1px solid {c['border']};
                border-radius: 5px; padding: 4px 8px;
                font-family: 'Consolas', 'Courier New', monospace; font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {c['accent']}; }}
            """
        )
        self.cmd_input.returnPressed.connect(self._run_command)
        input_row.addWidget(self.cmd_input, stretch=1)

        btn_run = QPushButton("▶")
        btn_run.setFixedSize(32, 32)
        btn_run.setStyleSheet(
            f"QPushButton {{ background:{c['accent']}; color:{c['bg']}; border:none; border-radius:5px; font-size:14px; }}"
            f"QPushButton:hover {{ background:{c['accent2']}; }}"
        )
        btn_run.clicked.connect(self._run_command)
        input_row.addWidget(btn_run)

        layout.addLayout(input_row)

    def _print_welcome(self):
        c = self.theme
        cwd = self.git.repo_path if self.git else "N/A"
        self._append(f"Supergit Terminal  —  {cwd}", "info")
        self._append("명령어를 입력하세요. ↑↓ 화살표로 이전 명령 탐색.", "muted")
        self._append("─" * 50, "border")

    def _append(self, text: str, kind: str = "normal"):
        c = self.theme
        colors = {
            "normal": c["fg"],
            "success": c["green"],
            "error": c["red"],
            "info": c["accent"],
            "muted": c["fg3"],
            "border": c["border"],
            "cmd": c["yellow"],
        }
        color = colors.get(kind, c["fg"])
        self.output.appendHtml(
            f'<span style="color:{color}; white-space:pre;">{self._escape(text)}</span>'
        )
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _escape(self, text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _run_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        self.cmd_input.add_history(cmd)
        self.cmd_input.clear()

        cwd = self.git.repo_path if self.git else "."
        self._append(f"$ {cmd}", "cmd")
        self.cmd_input.setEnabled(False)

        worker = CommandRunner(cmd, cwd)
        worker.done.connect(self._on_done)
        self._workers.append(worker)
        worker.start()

    def _on_done(self, output: str, success: bool):
        self._append(output, "success" if success else "error")
        self._append("", "normal")
        self.cmd_input.setEnabled(True)
        self.cmd_input.setFocus()

    def _clear(self):
        self.output.clear()
        self._print_welcome()
