"""Supergit 브랜치 탭"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QLineEdit, QMessageBox, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor


class WorkerThread(QThread):
    result = pyqtSignal(object)
    def __init__(self, fn, *args):
        super().__init__()
        self._fn = fn
        self._args = args
    def run(self):
        self.result.emit(self._fn(*self._args))


class BranchPanel(QWidget):
    def __init__(self, git_ops, i18n, theme, parent=None):
        super().__init__(parent)
        self.git = git_ops
        self.t = i18n
        self.theme = theme
        self._workers = []
        self._current = ""
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        c = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 현재 브랜치 표시
        cur_row = QHBoxLayout()
        lbl_cur_title = QLabel(self.t("branch_current") + ":")
        lbl_cur_title.setStyleSheet(f"color:{c['fg2']}; font-size:12px;")
        cur_row.addWidget(lbl_cur_title)
        self.lbl_current = QLabel()
        self.lbl_current.setStyleSheet(
            f"color:{c['accent']}; font-weight:bold; font-size:14px;"
        )
        cur_row.addWidget(self.lbl_current)
        cur_row.addStretch()
        btn_refresh = QPushButton(self.t("refresh"))
        btn_refresh.setFixedHeight(26)
        btn_refresh.setStyleSheet(self._btn_style(c['fg3']))
        btn_refresh.clicked.connect(self.refresh)
        cur_row.addWidget(btn_refresh)
        layout.addLayout(cur_row)

        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color:{c['border']};")
        layout.addWidget(line)

        # 새 브랜치 생성
        new_row = QHBoxLayout()
        new_row.setSpacing(6)
        self.new_branch_input = QLineEdit()
        self.new_branch_input.setPlaceholderText(self.t("branch_name"))
        self.new_branch_input.setFixedHeight(30)
        self.new_branch_input.setStyleSheet(self._input_style())
        self.new_branch_input.returnPressed.connect(self._create_branch)
        new_row.addWidget(self.new_branch_input)
        btn_create = QPushButton(self.t("create_branch"))
        btn_create.setFixedHeight(30)
        btn_create.setStyleSheet(self._btn_style(c['accent']))
        btn_create.clicked.connect(self._create_branch)
        new_row.addWidget(btn_create)
        layout.addLayout(new_row)

        # 로컬 브랜치 목록
        local_lbl = QLabel(self.t("branch_local"))
        local_lbl.setStyleSheet(
            f"color:{c['fg2']}; font-size:11px; font-weight:bold;"
        )
        layout.addWidget(local_lbl)

        self.local_list = QListWidget()
        self.local_list.setStyleSheet(self._list_style())
        self.local_list.itemDoubleClicked.connect(self._checkout_local)
        layout.addWidget(self.local_list)

        # 액션 버튼
        action_row = QHBoxLayout()
        action_row.setSpacing(6)
        for label, fn, col in [
            (self.t("checkout"), self._checkout_local_btn, c['accent']),
            (self.t("delete_branch"), self._delete_branch, c['red']),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(28)
            btn.setStyleSheet(self._btn_style(col))
            btn.clicked.connect(fn)
            action_row.addWidget(btn)
        action_row.addStretch()
        layout.addLayout(action_row)

        # 원격 브랜치
        remote_lbl = QLabel(self.t("branch_remote"))
        remote_lbl.setStyleSheet(
            f"color:{c['fg2']}; font-size:11px; font-weight:bold;"
        )
        layout.addWidget(remote_lbl)

        self.remote_list = QListWidget()
        self.remote_list.setStyleSheet(self._list_style())
        layout.addWidget(self.remote_list)

    def _btn_style(self, color: str):
        return f"""
        QPushButton {{
            background: transparent; color: {color}; border: 1px solid {color};
            border-radius: 5px; padding: 3px 12px; font-size: 12px;
        }}
        QPushButton:hover {{ background: {color}22; }}
        QPushButton:pressed {{ background: {color}44; }}
        """

    def _input_style(self):
        c = self.theme
        return f"""
        QLineEdit {{
            background: {c['bg2']}; color: {c['fg']}; border: 1px solid {c['border']};
            border-radius: 5px; padding: 4px 8px; font-size: 12px;
        }}
        QLineEdit:focus {{ border-color: {c['accent']}; }}
        """

    def _list_style(self):
        c = self.theme
        return f"""
        QListWidget {{
            background: {c['bg2']}; color: {c['fg']}; border: 1px solid {c['border']};
            border-radius: 6px; font-size: 12px; font-family: 'Consolas', monospace;
            outline: none;
        }}
        QListWidget::item {{ padding: 5px 8px; }}
        QListWidget::item:selected {{ background: {c['accent']}33; color: {c['accent']}; }}
        QListWidget::item:hover {{ background: {c['bg3']}; }}
        """

    def refresh(self):
        if not self.git:
            return
        w = WorkerThread(self.git.branches)
        w.result.connect(self._on_branches)
        self._workers.append(w)
        w.start()

    def _on_branches(self, data: dict):
        c = self.theme
        if "error" in data:
            return
        self._current = data.get("current", "")
        self.lbl_current.setText(f" {self._current}")

        self.local_list.clear()
        for b in data.get("local", []):
            item = QListWidgetItem(b)
            if b == self._current:
                item.setForeground(QColor(c["accent"]))
                item.setData(Qt.ItemDataRole.UserRole, "current")
                item.setText(f"* {b}")
            self.local_list.addItem(item)

        self.remote_list.clear()
        for b in data.get("remote", []):
            item = QListWidgetItem(b)
            item.setForeground(QColor(c["fg2"]))
            self.remote_list.addItem(item)

    def _checkout_local(self, item):
        name = item.text().lstrip("* ")
        if name == self._current:
            return
        ok, msg = self.git.checkout(name)
        if ok:
            self.refresh()
        else:
            QMessageBox.warning(self, self.t("error"), msg)

    def _checkout_local_btn(self):
        item = self.local_list.currentItem()
        if item:
            self._checkout_local(item)

    def _create_branch(self):
        name = self.new_branch_input.text().strip()
        if not name:
            return
        ok, msg = self.git.create_branch(name)
        if ok:
            self.new_branch_input.clear()
            self.refresh()
        else:
            QMessageBox.warning(self, self.t("error"), msg)

    def _delete_branch(self):
        item = self.local_list.currentItem()
        if not item:
            return
        name = item.text().lstrip("* ")
        if name == self._current:
            QMessageBox.warning(self, self.t("warning"), "현재 브랜치는 삭제할 수 없습니다.")
            return
        ok, msg = self.git.delete_branch(name)
        if ok:
            self.refresh()
        else:
            QMessageBox.warning(self, self.t("error"), msg)
