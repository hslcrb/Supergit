"""Supergit 커밋 히스토리 탭"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QPlainTextEdit, QSplitter, QHeaderView, QMessageBox,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class WorkerThread(QThread):
    result = pyqtSignal(object)
    def __init__(self, fn, *args):
        super().__init__()
        self._fn = fn
        self._args = args
    def run(self):
        self.result.emit(self._fn(*self._args))


class CommitPanel(QWidget):
    def __init__(self, git_ops, i18n, theme, parent=None):
        super().__init__(parent)
        self.git = git_ops
        self.t = i18n
        self.theme = theme
        self._workers = []
        self._commits = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        c = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # 헤더
        header = QHBoxLayout()
        title = QLabel(self.t("commit_history"))
        title.setStyleSheet(f"color:{c['fg']}; font-size:13px; font-weight:bold;")
        header.addWidget(title)
        header.addStretch()
        btn_refresh = QPushButton(self.t("refresh"))
        btn_refresh.setFixedHeight(26)
        btn_refresh.setStyleSheet(self._btn_style(c['fg3']))
        btn_refresh.clicked.connect(self.refresh)
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        # 스플리터
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {c['border']}; height: 2px; }}"
        )

        # 커밋 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            self.t("hash"), self.t("message"), self.t("author"),
            self.t("date"), ""
        ])
        self.table.horizontalHeader().setStyleSheet(
            f"QHeaderView::section {{ background:{c['bg2']}; color:{c['fg2']};"
            f"border:none; border-bottom:1px solid {c['border']}; padding:4px 8px; font-size:11px; }}"
        )
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background: {c['bg2']}; color: {c['fg']}; border: 1px solid {c['border']};
                border-radius: 6px; gridline-color: {c['border']}; font-size:12px;
                outline:none;
            }}
            QTableWidget::item {{ padding: 4px 8px; }}
            QTableWidget::item:selected {{ background:{c['accent']}33; color:{c['accent']}; }}
            """
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table.itemSelectionChanged.connect(self._on_select)
        splitter.addWidget(self.table)

        # 상세 패널 (diff / 메시지)
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 0, 0, 0)
        detail_layout.setSpacing(4)

        detail_lbl = QLabel(self.t("view_diff"))
        detail_lbl.setStyleSheet(f"color:{c['fg2']}; font-size:11px; font-weight:bold;")
        detail_layout.addWidget(detail_lbl)

        self.detail_view = QPlainTextEdit()
        self.detail_view.setReadOnly(True)
        self.detail_view.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background: {c['bg2']}; color: {c['fg']}; border: 1px solid {c['border']};
                border-radius: 6px; font-family: 'Consolas', monospace; font-size: 11px;
                padding: 6px;
            }}
            """
        )
        detail_layout.addWidget(self.detail_view)

        splitter.addWidget(detail_widget)
        splitter.setSizes([400, 150])
        layout.addWidget(splitter)

    def _btn_style(self, color: str):
        return f"""
        QPushButton {{
            background: transparent; color: {color}; border: 1px solid {color};
            border-radius: 5px; padding: 3px 12px; font-size: 12px;
        }}
        QPushButton:hover {{ background: {color}22; }}
        QPushButton:pressed {{ background: {color}44; }}
        """

    def refresh(self):
        if not self.git:
            return
        w = WorkerThread(self.git.log)
        w.result.connect(self._on_log)
        self._workers.append(w)
        w.start()

    def _on_log(self, commits: list):
        c = self.theme
        self._commits = commits
        self.table.setRowCount(len(commits))
        for row, commit in enumerate(commits):
            short = commit.get("short_hash", commit["hash"][:7])
            msg = commit.get("message", "")
            author = commit.get("author", "")
            date = commit.get("date", "")

            items = [short, msg, author, date]
            for col, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, col, item)

            # 체리픽 버튼
            btn = QPushButton(self.t("cherry_pick"))
            btn.setFixedHeight(22)
            btn.setStyleSheet(
                f"QPushButton {{ background:transparent; color:{c['orange']}; border:none; font-size:10px; }}"
                f"QPushButton:hover {{ color:{c['accent']}; }}"
            )
            btn.clicked.connect(lambda _, h=commit["hash"]: self._cherry_pick(h))
            self.table.setCellWidget(row, 4, btn)

        self.table.resizeRowsToContents()

    def _on_select(self):
        rows = self.table.selectedItems()
        if not rows:
            return
        row = self.table.currentRow()
        if row < 0 or row >= len(self._commits):
            return
        commit = self._commits[row]
        hash_ = commit.get("hash", "")
        out, err, code = "", "", 0
        try:
            import subprocess
            result = subprocess.run(
                ["git", "show", "--stat", hash_],
                cwd=self.git.repo_path, capture_output=True, text=True, timeout=10
            )
            text = result.stdout or result.stderr
        except Exception as e:
            text = str(e)
        self.detail_view.setPlainText(text)

    def _cherry_pick(self, hash_: str):
        ok, msg = self.git.cherry_pick(hash_)
        if ok:
            self.refresh()
        else:
            QMessageBox.warning(self, self.t("error"), msg)
