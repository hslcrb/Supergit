"""Supergit 설정 탭"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsPanel(QWidget):
    lang_changed = __import__('PyQt6.QtCore', fromlist=['pyqtSignal']).pyqtSignal(str)
    theme_changed = __import__('PyQt6.QtCore', fromlist=['pyqtSignal']).pyqtSignal(str)

    def __init__(self, i18n, theme, config, parent=None):
        super().__init__(parent)
        self.t = i18n
        self.theme = theme
        self.config = config
        self._setup_ui()

    def _setup_ui(self):
        c = self.theme
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 제목
        title = QLabel(self.t("tab_settings"))
        title.setStyleSheet(
            f"color:{c['fg']}; font-size:18px; font-weight:bold;"
        )
        layout.addWidget(title)

        sep = self._sep()
        layout.addWidget(sep)

        # 언어 선택
        lang_section = self._section(self.t("language"))
        layout.addWidget(lang_section)

        lang_row = QHBoxLayout()
        lang_row.setSpacing(8)
        self._lang_group = QButtonGroup(self)
        for code, label in [("ko", "한국어"), ("en", "English")]:
            btn = QRadioButton(label)
            btn.setStyleSheet(
                f"color:{c['fg']}; font-size:13px;"
                f"QRadioButton::indicator {{ width:14px; height:14px; }}"
            )
            if self.t.lang == code:
                btn.setChecked(True)
            btn.toggled.connect(lambda checked, lc=code: self._on_lang(checked, lc))
            self._lang_group.addButton(btn)
            lang_row.addWidget(btn)
        lang_row.addStretch()
        layout.addLayout(lang_row)

        sep2 = self._sep()
        layout.addWidget(sep2)

        # 테마 선택
        theme_section = self._section(self.t("theme"))
        layout.addWidget(theme_section)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(8)
        self._theme_group = QButtonGroup(self)
        cur_theme = self.config.get("theme", "dark")
        for code, label in [("dark", self.t("dark")), ("light", self.t("light"))]:
            btn = QRadioButton(label)
            btn.setStyleSheet(f"color:{c['fg']}; font-size:13px;")
            if cur_theme == code:
                btn.setChecked(True)
            btn.toggled.connect(lambda checked, tc=code: self._on_theme(checked, tc))
            self._theme_group.addButton(btn)
            theme_row.addWidget(btn)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        sep3 = self._sep()
        layout.addWidget(sep3)

        # 앱 정보
        about_section = self._section(self.t("about"))
        layout.addWidget(about_section)

        info_text = QLabel(
            f"<b>Supergit / 슈퍼깃</b><br>"
            f"{self.t('version')} 2.0.0 (Python + PyQt6)<br>"
            f"Git &amp; GitHub CLI GUI<br><br>"
            f"<span style='color:{c['fg3']}'>탭 단축키: Alt+1~5</span>"
        )
        info_text.setStyleSheet(f"color:{c['fg2']}; font-size:12px; line-height:1.6;")
        info_text.setOpenExternalLinks(True)
        layout.addWidget(info_text)

        layout.addStretch()

    def _sep(self):
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color:{self.theme['border']};")
        return f

    def _section(self, title: str):
        lbl = QLabel(title)
        lbl.setStyleSheet(
            f"color:{self.theme['fg2']}; font-size:11px; font-weight:bold; text-transform:uppercase; letter-spacing:1px;"
        )
        return lbl

    def _on_lang(self, checked: bool, code: str):
        if checked:
            self.lang_changed.emit(code)

    def _on_theme(self, checked: bool, code: str):
        if checked:
            self.theme_changed.emit(code)
