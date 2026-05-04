"""
MainWindow — assembles every panel, tab, toolbar and menu.
Handles all signal wiring between the sidebar, worker thread, and panels.
"""

import os
import numpy as np

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QFrame, QLabel, QAction, QToolBar,
    QFileDialog, QMessageBox, QProgressBar, QStatusBar, QPushButton
)
from PyQt5.QtCore import Qt, QSize

from ..io.image_io import load_image, save_image
from ..workers.processing_worker import ProcessingWorker
from .widgets import ImageCanvas
from .panels import MetadataPanel, PipelinePanel
from .sidebar import ToolsSidebar
from ..core.styles import DARK_STYLE, TOOLBAR_BTN_STYLE
from ..core.image_processor import ensure_gray
from ..DIP.zoom import bilinear_zoom, nearest_neighbor_zoom
from ..DIP.smoothing import apply_linear_filter, make_average_kernel, make_gaussian_kernel
from ..DIP.edge_detection import prewitt_edge, sobel_edge
from ..DIP.median import median_filter_scratch
from ..DIP.histogram_equalization import local_histogram_equalization


class MainWindow(QMainWindow):
    """
    Top-level application window.

    Responsibilities
    ----------------
    - Build and lay out all sub-widgets.
    - Wire sidebar signals → processing handlers.
    - Manage application state: current image, history stack, zoom state.
    - Dispatch heavy operations to ProcessingWorker (background thread).
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MedVision Workbench — Phase 1")
        self.resize(1400, 880)
        self.setStyleSheet(DARK_STYLE)

        # ── Application state ─────────────────────────────────────────────────
        self._original : np.ndarray | None = None   # unchanged loaded pixels
        self._current  : np.ndarray | None = None   # current processed image
        self._history  : list[np.ndarray]  = []     # undo pixel stack
        self._history_labels: list[str]    = []     # matching operation labels
        self._worker   : ProcessingWorker | None = None

        # Zoom state – always interpolate from _zoom_base at _zoom_factor
        self._zoom_base  : np.ndarray | None = None
        self._zoom_factor: float             = 1.0

        # ── Build UI ──────────────────────────────────────────────────────────
        self._build_menu()
        self._build_toolbar()
        self._build_central()
        self._build_statusbar()

    # =========================================================================
    #  UI CONSTRUCTION
    # =========================================================================

    def _build_menu(self):
        mb = self.menuBar()

        # File
        fm = mb.addMenu("File")
        self._add_action(fm, "Open Image…",          "Ctrl+O", self._open_file)
        self._add_action(fm, "Save Processed Image…","Ctrl+S", self._save_file)
        fm.addSeparator()
        self._add_action(fm, "Reset to Original",    "Ctrl+R", self._reset_to_original)
        fm.addSeparator()
        self._add_action(fm, "Quit",                 "Ctrl+Q", self.close)

        # Edit
        em = mb.addMenu("Edit")
        self._add_action(em, "Undo", "Ctrl+Z", self._undo)

        # View
        vm = mb.addMenu("View")
        self._add_action(vm, "Before / After Split", "",
                         lambda: self._tabs.setCurrentIndex(1))
        self._add_action(vm, "Edge View", "",
                         lambda: self._tabs.setCurrentIndex(2))

        # Help
        hm = mb.addMenu("Help")
        self._add_action(hm, "About MedVision", "", self._show_about)

    @staticmethod
    def _add_action(menu, label, shortcut, slot):
        a = QAction(label, menu.parent())
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(slot)
        menu.addAction(a)

    def _build_toolbar(self):
        tb = QToolBar("Main")
        tb.setIconSize(QSize(18, 18))
        tb.setMovable(False)
        self.addToolBar(tb)

        for label, tip, slot in [
            ("📂 Open",  "Open image file",       self._open_file),
            ("💾 Save",  "Save processed image",   self._save_file),
            ("↩ Undo",  "Undo last operation",    self._undo),
            ("⟳ Reset", "Reset to original image", self._reset_to_original),
        ]:
            btn = QPushButton(label)
            btn.setToolTip(tip)
            btn.setFixedHeight(28)
            btn.setStyleSheet(TOOLBAR_BTN_STYLE)
            btn.clicked.connect(slot)
            tb.addWidget(btn)
            if label in ("💾 Save", "⟳ Reset"):
                tb.addSeparator()

        # Progress bar sits in the toolbar (hidden until processing starts)
        self._progress = QProgressBar()
        self._progress.setFixedSize(120, 10)
        self._progress.setRange(0, 0)       # indeterminate spinner
        self._progress.setVisible(False)
        tb.addWidget(self._progress)

    def _build_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left: tools sidebar ───────────────────────────────────────────────
        self._sidebar = ToolsSidebar()
        self._sidebar.apply_filter .connect(self._on_apply_filter)
        self._sidebar.apply_zoom   .connect(self._on_apply_zoom)
        self._sidebar.apply_edge   .connect(self._on_apply_edge)
        self._sidebar.apply_hist_eq.connect(self._on_hist_eq)
        self._sidebar.apply_median .connect(self._on_median)

        # ── Centre: tab viewer ────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.currentChanged.connect(self._on_tab_changed)

        # Tab 0 — Processed result
        self._canvas_proc = ImageCanvas()
        self._tabs.addTab(self._canvas_proc, "Processed")

        # Tab 1 — Before / After split
        self._tabs.addTab(self._build_split_tab(), "Before / After")

        # Tab 2 — Edge component viewer (Gx | Gy | Magnitude)
        self._tabs.addTab(self._build_edge_tab(), "Edge View")

        # ── Right: metadata + pipeline ────────────────────────────────────────
        right_panel = QWidget()
        right_panel.setFixedWidth(230)
        rl = QVBoxLayout(right_panel)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._meta_panel = MetadataPanel()
        self._pipeline   = PipelinePanel()
        self._pipeline.undo_requested.connect(self._undo)

        rl.addWidget(self._meta_panel, 3)
        rl.addWidget(self._pipeline,   2)

        # ── Assemble root layout ──────────────────────────────────────────────
        root.addWidget(self._sidebar)
        root.addWidget(self._vline())
        root.addWidget(self._tabs, 1)
        root.addWidget(self._vline())
        root.addWidget(right_panel)

    def _build_split_tab(self) -> QWidget:
        """Two-column Before / After view."""
        w  = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(2)

        self._canvas_orig  = ImageCanvas()
        self._canvas_proc2 = ImageCanvas()

        for canvas, heading in [(self._canvas_orig,  "Original"),
                                 (self._canvas_proc2, "Processed")]:
            col = QVBoxLayout()
            lbl = QLabel(heading)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#4a6080; font-size:10px; background:#0a0c10;")
            col.addWidget(lbl)
            col.addWidget(canvas)
            hl.addLayout(col)

        return w

    def _build_edge_tab(self) -> QWidget:
        """Three-column edge component viewer."""
        w  = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(2)

        self._canvas_gx   = ImageCanvas()
        self._canvas_gy   = ImageCanvas()
        self._canvas_edge = ImageCanvas()

        for canvas, heading in [(self._canvas_gx,   "Gx  (Horizontal)"),
                                 (self._canvas_gy,   "Gy  (Vertical)"),
                                 (self._canvas_edge, "Magnitude")]:
            col = QVBoxLayout()
            lbl = QLabel(heading)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#4a6080; font-size:10px; background:#0a0c10;")
            col.addWidget(lbl)
            col.addWidget(canvas)
            hl.addLayout(col)

        return w

    def _build_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status_label = QLabel("Ready — Open an image to begin.")
        self._status_label.setStyleSheet("color: #4a6080; padding: 0 8px;")
        sb.addWidget(self._status_label)

    @staticmethod
    def _vline() -> QFrame:
        """Thin vertical separator line."""
        f = QFrame()
        f.setFrameShape(QFrame.VLine)
        f.setStyleSheet("color: #1a2030;")
        return f

    # =========================================================================
    #  STATUS BAR HELPER
    # =========================================================================

    def _set_status(self, msg: str):
        self._status_label.setText(msg)

    # =========================================================================
    #  FILE I/O
    # =========================================================================

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Medical Image", "",
            "All Images (*.dcm *.dicom *.jpg *.jpeg *.bmp *.png *.tif *.tiff);;"
            "DICOM (*.dcm *.dicom);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)"
        )
        if not path:
            return
        try:
            result = load_image(path)
            if result.error:
                QMessageBox.critical(self, "Load Error", result.error)
                return
            if result.pixel_array is None:
                QMessageBox.critical(self, "Load Error", "Could not decode image pixels.")
                return

            self._original = result.pixel_array.copy()
            self._current  = result.pixel_array.copy()
            self._history.clear()
            self._history_labels.clear()
            self._pipeline.clear()
            self._zoom_base   = None
            self._zoom_factor = 1.0

            self._update_canvases()
            self._meta_panel.set_metadata(result.metadata)
            self._meta_panel.histogram.set_array(self._current)
            self._set_status(
                f"Loaded: {os.path.basename(path)}  "
                f"({result.metadata.get('Width','?')} × "
                f"{result.metadata.get('Height','?')})  "
                f"Format: {result.format}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", str(e))

    def _save_file(self):
        if self._current is None:
            QMessageBox.information(self, "No Image", "No processed image to save.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Processed Image", "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp)"
        )
        if not path:
            return
        err = save_image(self._current, path)
        if err:
            QMessageBox.critical(self, "Save Error", err)
        else:
            self._set_status(f"Saved: {os.path.basename(path)}")

    # =========================================================================
    #  STATE MANAGEMENT
    # =========================================================================

    def _push_history(self, label: str):
        """Snapshot current image onto the undo stack before an operation."""
        if self._current is not None:
            self._history.append(self._current.copy())
            self._history_labels.append(label)

    def _undo(self):
        if not self._history:
            self._set_status("Nothing to undo.")
            return
        self._current = self._history.pop()
        label = self._history_labels.pop() if self._history_labels else "?"
        self._pipeline.remove_last()
        self._zoom_base   = None
        self._zoom_factor = 1.0
        self._update_canvases()
        self._meta_panel.histogram.set_array(self._current)
        self._set_status(f"Undone: {label}")

    def _reset_to_original(self):
        if self._original is None:
            return
        self._current = self._original.copy()
        self._history.clear()
        self._history_labels.clear()
        self._pipeline.clear()
        self._zoom_base   = None
        self._zoom_factor = 1.0
        self._update_canvases()
        self._meta_panel.histogram.set_array(self._current)
        self._set_status("Reset to original.")

    def _update_canvases(self):
        if self._current is None:
            return
        self._canvas_proc.set_array(self._current)
        self._canvas_proc2.set_array(self._current)
        if self._original is not None:
            self._canvas_orig.set_array(self._original)

    def _on_tab_changed(self, _index: int):
        self._update_canvases()

    # =========================================================================
    #  PROCESSING DISPATCH
    # =========================================================================

    def _require_image(self) -> bool:
        if self._current is None:
            QMessageBox.information(self, "No Image", "Please open an image first.")
            return False
        return True

    def _start_worker(self, func, label: str, *args, **kwargs):
        """Push history, show progress bar, launch background worker."""
        if self._worker and self._worker.isRunning():
            self._set_status("Processing in progress — please wait…")
            return
        self._push_history(label)
        self._progress.setVisible(True)
        self._worker = ProcessingWorker(func, label, *args, **kwargs)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error   .connect(self._on_worker_error)
        self._worker.start()
        self._set_status(f"Processing: {label}…")

    def _on_worker_finished(self, result: np.ndarray, label: str):
        self._current = result
        self._pipeline.add_step(label)
        # Non-zoom operations invalidate the zoom base so the next zoom
        # starts fresh from the newly processed image.
        if "Zoom" not in label:
            self._zoom_base   = None
            self._zoom_factor = 1.0
        self._update_canvases()
        self._meta_panel.histogram.set_array(self._current)
        self._progress.setVisible(False)
        self._set_status(
            f"Done: {label}  —  {result.shape[1]}×{result.shape[0]} px"
        )

    def _on_worker_error(self, msg: str):
        self._progress.setVisible(False)
        # Roll back the history push that happened before the worker started
        if self._history:
            self._current = self._history.pop()
            if self._history_labels:
                self._history_labels.pop()
        QMessageBox.critical(self, "Processing Error", msg)
        self._set_status("Error during processing.")

    # =========================================================================
    #  TOOL SIGNAL HANDLERS
    # =========================================================================

    def _on_apply_zoom(self, step: float, method: str):
        if not self._require_image():
            return

        # First zoom in this sequence → snapshot the current image as the base
        if self._zoom_base is None:
            self._zoom_base   = self._current.copy()
            self._zoom_factor = 1.0

        new_factor = max(0.05, min(16.0, self._zoom_factor * step))
        if new_factor == self._zoom_factor:
            self._set_status("Zoom limit reached.")
            return

        self._zoom_factor = new_factor
        direction = "In" if step >= 1.0 else "Out"
        label     = (f"Zoom {direction} ({method.split('-')[0]}) "
                     f"— {self._zoom_factor:.2f}×")

        zoom_func     = bilinear_zoom if method == "Bilinear" else nearest_neighbor_zoom
        base_snapshot = self._zoom_base.copy()
        factor        = self._zoom_factor

        # Always interpolate from the clean base — never from the zoomed array
        self._start_worker(zoom_func, label, base_snapshot, factor)

    def _on_apply_filter(self, filter_name: str, params: dict):
        if not self._require_image():
            return
        ks = params.get("kernel_size", 3)

        if filter_name == "average":
            kernel = make_average_kernel(ks)
            label  = f"Average Filter {ks}×{ks}"
        elif filter_name == "gaussian":
            sigma  = params.get("sigma", 1.0)
            kernel = make_gaussian_kernel(ks, sigma)
            label  = f"Gaussian Filter {ks}×{ks}  σ={sigma:.1f}"
        else:
            return

        self._start_worker(apply_linear_filter, label, self._current, kernel)

    def _on_apply_edge(self, operator: str, component: str):
        if not self._require_image():
            return

        gray = ensure_gray(self._current)
        if operator == "Sobel":
            Gx, Gy, mag = sobel_edge(gray)
        else:
            Gx, Gy, mag = prewitt_edge(gray)

        # Fill the three-panel Edge View tab
        self._canvas_gx  .set_array(Gx)
        self._canvas_gy  .set_array(Gy)
        self._canvas_edge.set_array(mag)
        self._tabs.setCurrentIndex(2)

        # Choose which component becomes the new _current
        result = {"Magnitude": mag, "Horizontal (Gx)": Gx, "Vertical (Gy)": Gy
                  }.get(component, mag)
        label  = f"{operator} Edge ({component})"

        self._push_history(label)
        self._current = result
        self._zoom_base   = None
        self._zoom_factor = 1.0
        self._pipeline.add_step(label)
        self._meta_panel.histogram.set_array(self._current)
        self._update_canvases()
        self._set_status(f"Done: {label}")

    def _on_hist_eq(self, block_size: int):
        if not self._require_image():
            return
        gray  = ensure_gray(self._current)
        label = f"Local Hist. Eq. {block_size}×{block_size}"
        self._start_worker(local_histogram_equalization, label, gray, block_size)

    def _on_median(self, kernel_size: int):
        if not self._require_image():
            return
        label = f"Median Filter {kernel_size}×{kernel_size}"
        self._start_worker(median_filter_scratch, label, self._current, kernel_size)

    # =========================================================================
    #  ABOUT DIALOG
    # =========================================================================

    def _show_about(self):
        QMessageBox.about(
            self, "About MedVision Workbench",
            "<b style='font-size:14px'>MedVision Workbench</b><br>"
            "<i>Phase 1 — Spatial Domain Operations</i><br><br>"
            "• Multi-format I/O: DICOM, JPEG, BMP, PNG<br>"
            "• Custom 2-D convolution (from scratch)<br>"
            "• Nearest-Neighbor &amp; Bilinear zoom (from scratch)<br>"
            "• Average, Gaussian, Median filtering (from scratch)<br>"
            "• Sobel &amp; Prewitt edge detection (from scratch)<br>"
            "• Local Histogram Equalization (from scratch)<br>"
            "• Sequential Enhancement Pipeline with undo<br><br>"
            "Cairo University — Biomedical Engineering"
        )