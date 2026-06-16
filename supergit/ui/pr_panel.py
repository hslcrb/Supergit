"""Supergit PR 탭"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QPlainTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from ..git_ops import gh_installed, gh_create_pr, gh_list_prs


class WorkerThread(QThread):
    result = pyqtSignal(object)
    def __init__(self, fn, *args):
        super().__init__()
        self._fn = fn
        self._args = args
    def run(self):
        self.result.emit(self._fn(*self._args))


class PRPanel(QWidget):
    def __init__(self, git_ops, i18n, theme, parent=None):
        super().__init__(parent)
        self.git = git_ops
        self.t = i18n
        self.theme = theme
        self._workers = []
        self._gh_ok = False
        self._setup_ui()
        self._check_gh()

    def _setup_ui(self):
        c = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # gh 상태 표시
        self.gh_banner = QLabel()
        self.gh_banner.setStyleSheet(
            f"color:{c['yellow']}; background:{c['bg2']}; border:1px solid {c['yellow']}33;"
            f"border-radius:5px; padding:6px 12px; font-size:11px;"
        )
        self.gh_banner.hide()
        layout.addWidget(self.gh_banner)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background:{c['border']}; width:2px; }}"
        )

        # ─ 왼쪽: PR 생성 폼 ─
        form = QWidget()
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(0, 0, 8, 0)
        form_layout.setSpacing(8)

        form_title = QLabel(self.t("create_pr"))
        form_title.setStyleSheet(f"color:{c['fg']}; font-size:13px; font-weight:bold;")
        form_layout.addWidget(form_title)

        for attr, key in [
            ("_pr_title", "pr_title"),
            ("_pr_base", "base_branch"),
            ("_pr_head", "head_branch"),
        ]:
            lbl = QLabel(self.t(key))
            lbl.setStyleSheet(f"color:{c['fg2']}; font-size:11px;")
            form_layout.addWidget(lbl)
            inp = QLineEdit()
            inp.setFixedHeight(30)
            inp.setStyleSheet(self._input_style())
            form_layout.addWidget(inp)
            setattr(self, attr, inp)

        body_lbl = QLabel(self.t("pr_body"))
        body_lbl.setStyleSheet(f"color:{c['fg2']}; font-size:11px;")
        form_layout.addWidget(body_lbl)

        self._pr_body = QPlainTextEdit()
        self._pr_body.setMaximumHeight(100)
        self._pr_body.setStyleSheet(
            f"QPlainTextEdit {{ background:{c['bg2']}; color:{c['fg']}; border:1px solid {c['border']};"
            f"border-radius:5px; padding:6px; font-size:12px; }}"
            f"QPlainTextEdit:focus {{ border-color:{c['accent']}; }}"
        )
        form_layout.addWidget(self._pr_body)

        btn_create = QPushButton(self.t("create_pr"))
        btn_create.setFixedHeight(32)
        btn_create.setStyleSheet(self._btn_style(c['accent'], bold=True))
        btn_create.clicked.connect(self._create_pr)
        form_layout.addWidget(btn_create)
        form_layout.addStretch()

        splitter.addWidget(form)

        # ─ 오른쪽: PR 목록 ─
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(8, 0, 0, 0)
        list_layout.setSpacing(8)

        list_hdr = QHBoxLayout()
        list_title = QLabel(self.t("pr_list"))
        list_title.setStyleSheet(f"color:{c['fg']}; font-size:13px; font-weight:bold;")
        list_hdr.addWidget(list_title)
        list_hdr.addStretch()
        btn_refresh = QPushButton(self.t("refresh"))
        btn_refresh.setFixedHeight(26)
        btn_refresh.setStyleSheet(self._btn_style(c['fg3']))
        btn_refresh.clicked.connect(self._load_prs)
        list_hdr.addWidget(btn_refresh)
        list_layout.addLayout(list_hdr)

        self.pr_table = QTableWidget()
        self.pr_table.setColumnCount(4)
        self.pr_table.setHorizontalHeaderLabels(["#", self.t("pr_title"), "State", "Author"])
        self.pr_table.horizontalHeader().setStyleSheet(
            f"QHeaderView::section {{ background:{c['bg2']}; color:{c['fg2']};"
            f"border:none; border-bottom:1px solid {c['border']}; padding:4px; font-size:11px; }}"
        )
        self.pr_table.setStyleSheet(
            f"QTableWidget {{ background:{c['bg2']}; color:{c['fg']}; border:1px solid {c['border']};"
            f"border-radius:6px; gridline-color:{c['border']}; font-size:12px; outline:none; }}"
            f"QTableWidget::item {{ padding:4px 6px; }}"
            f"QTableWidget::item:selected {{ background:{c['accent']}33; color:{c['accent']}; }}"
        )
        self.pr_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pr_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.pr_table.verticalHeader().setVisible(False)
        hdr = self.pr_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        list_layout.addWidget(self.pr_table)

        splitter.addWidget(list_widget)
        splitter.setSizes([350, 400])
        layout.addWidget(splitter)

    def _btn_style(self, color: str, bold: bool = False):
        weight = "bold" if bold else "normal"
        return f"""
        QPushButton {{
            background: transparent; color: {color}; border: 1px solid {color};
            border-radius: 5px; padding: 3px 12px; font-size: 12px; font-weight: {weight};
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

    def _check_gh(self):
        self._gh_ok = gh_installed()
        if not self._gh_ok:
            self.gh_banner.setText(
                f"⚠  {self.t('gh_not_installed')}  —  {self.t('gh_install_hint')}"
            )
            self.gh_banner.show()
        else:
            self._load_prs()

    def _load_prs(self):
        if not self._gh_ok or not self.git:
            return
        w = WorkerThread(gh_list_prs, self.git.repo_path)
        w.result.connect(self._on_prs)
        self._workers.append(w)
        w.start()

    def _on_prs(self, data):
        ok, prs = data
        if not ok:
            return
        c = self.theme
        self.pr_table.setRowCount(len(prs))
        state_colors = {"OPEN": c["green"], "CLOSED": c["red"], "MERGED": c["accent"]}
        for row, pr in enumerate(prs):
            num = QTableWidgetItem(f"#{pr.get('number', '')}")
            title = QTableWidgetItem(pr.get("title", ""))
            state = pr.get("state", "")
            state_item = QTableWidgetItem(state)
            state_item.setForeground(QColor(state_colors.get(state, c["fg"])))
            author_data = pr.get("author", {})
            author = author_data.get("login", "") if isinstance(author_data, dict) else str(author_data)
            author_item = QTableWidgetItem(author)

            for col, item in enumerate([num, title, state_item, author_item]):
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.pr_table.setItem(row, col, item)

    def _create_pr(self):
        if not self._gh_ok or not self.git:
            return
        title = self._pr_title.text().strip()
        body = self._pr_body.toPlainText().strip()
        base = self._pr_base.text().strip()
        head = self._pr_head.text().strip()
        if not title or not base or not head:
            return
        ok, msg = gh_create_pr(self.git.repo_path, title, body, base, head)
        if ok:
            self._pr_title.clear()
            self._pr_body.clear()
            self._load_prs()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.t("error"), msg)
