"""Supergit 상태 탭 (Status Panel)"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QPlainTextEdit, QSplitter, QMessageBox, QFrame,
    QScrollArea, QSizePolicy, QToolButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor


class WorkerThread(QThread):
    result = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, fn, *args):
        super().__init__()
        self._fn = fn
        self._args = args

    def run(self):
        try:
            self.result.emit(self._fn(*self._args))
        except Exception as e:
            self.error.emit(str(e))


class FileItem(QListWidgetItem):
    def __init__(self, path: str, change_type: str = "", is_untracked: bool = False):
        super().__init__()
        self.filepath = path
        self.change_type = change_type
        self.is_untracked = is_untracked
        label = path
        if change_type:
            label = f"[{change_type}] {path}"
        elif is_untracked:
            label = f"[?] {path}"
        self.setText(label)


class StatusPanel(QWidget):
    def __init__(self, git_ops, i18n, theme, parent=None):
        super().__init__(parent)
        self.git = git_ops
        self.t = i18n
        self.theme = theme
        self._workers = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        c = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ─ 상단 액션 바 ─
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)

        self.lbl_branch = QLabel()
        self.lbl_branch.setStyleSheet(
            f"color:{c['accent']}; font-weight:bold; font-size:13px;"
        )
        top_bar.addWidget(self.lbl_branch)

        self.lbl_ahead = QLabel()
        self.lbl_ahead.setStyleSheet(f"color:{c['green']}; font-size:11px;")
        top_bar.addWidget(self.lbl_ahead)

        top_bar.addStretch()

        for key, fn, col in [
            ("fetch", self._fetch, c['fg2']),
            ("pull", self._pull, c['accent']),
            ("push", self._push, c['green']),
            ("refresh", self.refresh, c['fg3']),
        ]:
            btn = QPushButton(self.t(key))
            btn.setFixedHeight(28)
            btn.setStyleSheet(self._btn_style(col))
            btn.clicked.connect(fn)
            top_bar.addWidget(btn)

        layout.addLayout(top_bar)

        # ─ 상태 라벨 ─
        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet(f"color:{c['fg3']}; font-size:11px;")
        layout.addWidget(self.lbl_status)

        # ─ 스플리터: 파일 목록 | 커밋 영역 ─
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {c['border']}; height:2px; }}"
        )

        # ─ 파일 목록 (staged / unstaged) ─
        files_widget = QWidget()
        files_layout = QVBoxLayout(files_widget)
        files_layout.setContentsMargins(0, 0, 0, 0)
        files_layout.setSpacing(6)

        # staged
        staged_header = QHBoxLayout()
        staged_lbl = QLabel(self.t("staged"))
        staged_lbl.setStyleSheet(
            f"color:{c['fg2']}; font-size:11px; font-weight:bold; text-transform:uppercase;"
        )
        staged_header.addWidget(staged_lbl)
        staged_header.addStretch()

        btn_stage_all = QPushButton(self.t("stage_all"))
        btn_stage_all.setFixedHeight(22)
        btn_stage_all.setStyleSheet(self._small_btn_style(c['accent']))
        btn_stage_all.clicked.connect(self._stage_all)
        staged_header.addWidget(btn_stage_all)

        btn_unstage_all = QPushButton(self.t("unstage_all"))
        btn_unstage_all.setFixedHeight(22)
        btn_unstage_all.setStyleSheet(self._small_btn_style(c['red']))
        btn_unstage_all.clicked.connect(self._unstage_all)
        staged_header.addWidget(btn_unstage_all)

        files_layout.addLayout(staged_header)

        self.staged_list = QListWidget()
        self.staged_list.setStyleSheet(self._list_style())
        self.staged_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.staged_list.customContextMenuRequested.connect(self._staged_context)
        self.staged_list.itemDoubleClicked.connect(lambda item: self._unstage(item))
        files_layout.addWidget(self.staged_list)

        # unstaged
        unstaged_header = QHBoxLayout()
        unstaged_lbl = QLabel(self.t("unstaged"))
        unstaged_lbl.setStyleSheet(
            f"color:{c['fg2']}; font-size:11px; font-weight:bold; text-transform:uppercase;"
        )
        unstaged_header.addWidget(unstaged_lbl)
        unstaged_header.addStretch()
        files_layout.addLayout(unstaged_header)

        self.unstaged_list = QListWidget()
        self.unstaged_list.setStyleSheet(self._list_style())
        self.unstaged_list.itemDoubleClicked.connect(lambda item: self._stage(item))
        files_layout.addWidget(self.unstaged_list)

        splitter.addWidget(files_widget)

        # ─ 커밋 영역 ─
        commit_widget = QWidget()
        commit_layout = QVBoxLayout(commit_widget)
        commit_layout.setContentsMargins(0, 0, 0, 0)
        commit_layout.setSpacing(6)

        commit_lbl = QLabel(self.t("commit_msg"))
        commit_lbl.setStyleSheet(
            f"color:{c['fg2']}; font-size:11px; font-weight:bold; text-transform:uppercase;"
        )
        commit_layout.addWidget(commit_lbl)

        self.commit_input = QPlainTextEdit()
        self.commit_input.setPlaceholderText(self.t("commit_msg") + "...")
        self.commit_input.setMaximumHeight(80)
        self.commit_input.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background:{c['bg2']}; color:{c['fg']}; border:1px solid {c['border']};
                border-radius:6px; padding:6px; font-family:'Consolas','Noto Sans KR',monospace;
                font-size:12px;
            }}
            QPlainTextEdit:focus {{ border-color:{c['accent']}; }}
            """
        )
        commit_layout.addWidget(self.commit_input)

        btn_commit = QPushButton(self.t("commit"))
        btn_commit.setFixedHeight(32)
        btn_commit.setStyleSheet(self._btn_style(c['accent'], bold=True))
        btn_commit.clicked.connect(self._commit)
        commit_layout.addWidget(btn_commit)

        splitter.addWidget(commit_widget)
        splitter.setSizes([350, 150])

        layout.addWidget(splitter)

    # ─ 스타일 헬퍼 ─

    def _btn_style(self, color: str, bold: bool = False):
        c = self.theme
        weight = "bold" if bold else "normal"
        return f"""
        QPushButton {{
            background: transparent; color: {color}; border: 1px solid {color};
            border-radius: 5px; padding: 3px 12px; font-size: 12px; font-weight: {weight};
        }}
        QPushButton:hover {{ background: {color}22; }}
        QPushButton:pressed {{ background: {color}44; }}
        """

    def _small_btn_style(self, color: str):
        return f"""
        QPushButton {{
            background: transparent; color: {color}; border: none;
            font-size: 11px; padding: 1px 6px;
        }}
        QPushButton:hover {{ background: {color}22; border-radius: 3px; }}
        """

    def _list_style(self):
        c = self.theme
        return f"""
        QListWidget {{
            background: {c['bg2']}; color: {c['fg']}; border: 1px solid {c['border']};
            border-radius: 6px; font-size: 12px; font-family: 'Consolas', monospace;
            outline: none;
        }}
        QListWidget::item {{ padding: 4px 8px; }}
        QListWidget::item:selected {{ background: {c['accent']}33; color: {c['accent']}; }}
        QListWidget::item:hover {{ background: {c['bg3']}; }}
        """

    # ─ Git 작업 ─

    def refresh(self):
        if not self.git:
            return
        self.lbl_status.setText(self.t("loading"))
        w = WorkerThread(self.git.status)
        w.result.connect(self._on_status)
        w.error.connect(lambda e: self.lbl_status.setText(f"오류: {e}"))
        self._workers.append(w)
        w.start()

    def _on_status(self, data: dict):
        c = self.theme
        if "error" in data:
            self.lbl_status.setText(data["error"])
            return

        branch = data.get("current", "")
        self.lbl_branch.setText(f"  {branch}")

        ahead = data.get("ahead", 0)
        behind = data.get("behind", 0)
        parts = []
        if ahead:
            parts.append(f"↑{ahead}")
        if behind:
            parts.append(f"↓{behind}")
        self.lbl_ahead.setText("  ".join(parts))

        self.staged_list.clear()
        staged = data.get("staged", [])
        for f in staged:
            item = FileItem(f["path"], f.get("change_type", "M"))
            item.setForeground(QColor(c["green"]))
            self.staged_list.addItem(item)

        self.unstaged_list.clear()
        for f in data.get("unstaged", []):
            item = FileItem(f["path"], f.get("change_type", "M"))
            item.setForeground(QColor(c["red"]))
            self.unstaged_list.addItem(item)
        for f in data.get("untracked", []):
            item = FileItem(f, "", is_untracked=True)
            item.setForeground(QColor(c["yellow"]))
            self.unstaged_list.addItem(item)

        total = len(staged) + len(data.get("unstaged", [])) + len(data.get("untracked", []))
        if total == 0:
            self.lbl_status.setText(f"  {self.t('clean_tree')}")
        else:
            self.lbl_status.setText(
                f"  staged: {len(staged)}  unstaged: {len(data.get('unstaged', []))}  untracked: {len(data.get('untracked', []))}"
            )

    def _stage(self, item):
        if not isinstance(item, FileItem):
            return
        ok, msg = self.git.stage_file(item.filepath)
        self.refresh()

    def _unstage(self, item):
        if not isinstance(item, FileItem):
            return
        ok, msg = self.git.unstage_file(item.filepath)
        self.refresh()

    def _stage_all(self):
        ok, msg = self.git.stage_all()
        self.refresh()

    def _unstage_all(self):
        ok, msg = self.git.unstage_all()
        self.refresh()

    def _staged_context(self, pos):
        item = self.staged_list.itemAt(pos)
        if item:
            self._unstage(item)

    def _commit(self):
        msg = self.commit_input.toPlainText().strip()
        if not msg:
            return
        ok, out = self.git.commit(msg)
        if ok:
            self.commit_input.clear()
            self.refresh()
        else:
            QMessageBox.warning(self, self.t("error"), out)

    def _push(self):
        ok, out = self.git.push()
        if not ok:
            QMessageBox.warning(self, self.t("error"), out)
        else:
            self.refresh()

    def _pull(self):
        ok, out = self.git.pull()
        if not ok:
            QMessageBox.warning(self, self.t("error"), out)
        else:
            self.refresh()

    def _fetch(self):
        ok, out = self.git.fetch()
        self.refresh()

    def update_theme(self, theme, i18n):
        self.theme = theme
        self.t = i18n
        # 재구성
        for i in reversed(range(self.layout().count())):
            w = self.layout().itemAt(i).widget()
            if w:
                w.deleteLater()
        self._setup_ui()
        self.refresh()
