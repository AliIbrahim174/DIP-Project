"""
Right-side dock panels:
  - MetadataPanel  — displays image metadata as HTML + live histogram
  - PipelinePanel  — sequential enhancement log with undo button
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import pyqtSignal

from .widgets import HistogramWidget
from ..core.styles import (
    ACCENT, PIPELINE_LIST_STYLE, PIPELINE_UNDO_STYLE, METADATA_TEXT_STYLE
)


# ─────────────────────────────────────────────────────────────────────────────
#  METADATA PANEL
# ─────────────────────────────────────────────────────────────────────────────

class MetadataPanel(QWidget):
    """
    Displays image metadata (width, height, bit-depth, DICOM tags, …)
    as a styled HTML list, plus a live luminance histogram below it.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # ── Header ────────────────────────────────────────────────────────────
        title = QLabel("ℹ  Metadata")
        title.setStyleSheet(f"color: {ACCENT}; font-weight: bold; font-size: 11px;")
        layout.addWidget(title)

        # ── Key-value text area ───────────────────────────────────────────────
        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setStyleSheet(METADATA_TEXT_STYLE)
        layout.addWidget(self._text)

        # ── Histogram header ──────────────────────────────────────────────────
        hist_title = QLabel("📊  Histogram")
        hist_title.setStyleSheet(
            f"color: {ACCENT}; font-weight: bold; font-size: 11px; margin-top: 4px;"
        )
        layout.addWidget(hist_title)

        # ── Histogram canvas ──────────────────────────────────────────────────
        self.histogram = HistogramWidget()
        layout.addWidget(self.histogram)

    def set_metadata(self, meta: dict) -> None:
        """Render a dict of {label: value} as colour-coded HTML."""
        lines = [
            f"<b style='color:{ACCENT}'>{k}</b>: {v}"
            for k, v in meta.items()
        ]
        self._text.setHtml("<br>".join(lines))

    def clear(self) -> None:
        self._text.clear()


# ─────────────────────────────────────────────────────────────────────────────
#  PIPELINE PANEL
# ─────────────────────────────────────────────────────────────────────────────

class PipelinePanel(QWidget):
    """
    Numbered list of applied operations representing the sequential
    enhancement pipeline.  Emits undo_requested when the Undo button
    is clicked.
    """

    undo_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # ── Header ────────────────────────────────────────────────────────────
        title = QLabel("⚙  Pipeline")
        title.setStyleSheet(f"color: {ACCENT}; font-weight: bold; font-size: 11px;")
        layout.addWidget(title)

        # ── Step list ─────────────────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setStyleSheet(PIPELINE_LIST_STYLE)
        layout.addWidget(self._list)

        # ── Undo button ───────────────────────────────────────────────────────
        self._undo_btn = QPushButton("↩  Undo Last")
        self._undo_btn.setStyleSheet(PIPELINE_UNDO_STYLE)
        self._undo_btn.clicked.connect(self.undo_requested)
        layout.addWidget(self._undo_btn)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_step(self, label: str) -> None:
        """Append a numbered step entry and scroll to it."""
        n    = self._list.count() + 1
        item = QListWidgetItem(f"{n}. {label}")
        self._list.addItem(item)
        self._list.scrollToBottom()

    def remove_last(self) -> None:
        """Remove the most recently added step (used by undo)."""
        row = self._list.count() - 1
        if row >= 0:
            self._list.takeItem(row)

    def clear(self) -> None:
        """Remove all steps."""
        self._list.clear()