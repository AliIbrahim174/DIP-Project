"""
Left-side tools sidebar containing all user controls:
  - Zoom / Interpolation
  - Smoothing Filters  (Average, Gaussian)
  - Edge Detection     (Sobel, Prewitt)
  - Median Filter
  - Local Histogram Equalization
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QDoubleSpinBox, QScrollArea
)
from PyQt5.QtCore import pyqtSignal

from ..core.styles import SIDEBAR_STYLE


class ToolsSidebar(QWidget):
    """
    Emits signals whenever the user requests an operation.
    The MainWindow connects these to the processing dispatch layer,
    keeping UI logic cleanly separated from business logic.

    Signals
    -------
    apply_filter(str, dict)     filter_name, params dict
    apply_zoom(float, str)      step multiplier, interpolation method name
    apply_edge(str, str)        operator name, component name
    apply_hist_eq(int)          block size
    apply_median(int)           kernel size
    """

    apply_filter  = pyqtSignal(str, dict)
    apply_zoom    = pyqtSignal(float, str)
    apply_edge    = pyqtSignal(str, str)
    apply_hist_eq = pyqtSignal(int)
    apply_median  = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet(SIDEBAR_STYLE)

        # Wrap everything in a scroll area so it never clips on small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        layout    = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        layout.addWidget(self._build_zoom_group())
        layout.addWidget(self._build_smoothing_group())
        layout.addWidget(self._build_edge_group())
        layout.addWidget(self._build_median_group())
        layout.addWidget(self._build_histeq_group())
        layout.addStretch()

        scroll.setWidget(container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ── Group builders ────────────────────────────────────────────────────────

    def _build_zoom_group(self) -> QGroupBox:
        g  = QGroupBox("Zoom / Interpolation")
        gl = QVBoxLayout(g)
        gl.setSpacing(3)

        # Method selector
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Method:"))
        self._zoom_method = QComboBox()
        self._zoom_method.addItems(["Nearest-Neighbor", "Bilinear"])
        r1.addWidget(self._zoom_method)
        gl.addLayout(r1)

        # Step scale
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Step ×:"))
        self._zoom_scale = QDoubleSpinBox()
        self._zoom_scale.setRange(1.1, 8.0)
        self._zoom_scale.setSingleStep(0.25)
        self._zoom_scale.setValue(1.5)
        r2.addWidget(self._zoom_scale)
        gl.addLayout(r2)

        btn_in  = QPushButton("⊕  Zoom In")
        btn_out = QPushButton("⊖  Zoom Out")
        btn_in .clicked.connect(
            lambda: self.apply_zoom.emit(self._zoom_scale.value(),
                                         self._zoom_method.currentText()))
        btn_out.clicked.connect(
            lambda: self.apply_zoom.emit(1.0 / self._zoom_scale.value(),
                                         self._zoom_method.currentText()))
        gl.addWidget(btn_in)
        gl.addWidget(btn_out)
        return g

    def _build_smoothing_group(self) -> QGroupBox:
        g  = QGroupBox("Smoothing Filters")
        sl = QVBoxLayout(g)
        sl.setSpacing(3)

        # Kernel size
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Kernel:"))
        self._smooth_kernel = QComboBox()
        self._smooth_kernel.addItems(["3×3", "5×5", "7×7", "9×9", "11×11"])
        r1.addWidget(self._smooth_kernel)
        sl.addLayout(r1)

        # Gaussian sigma
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Gauss σ:"))
        self._gauss_sigma = QDoubleSpinBox()
        self._gauss_sigma.setRange(0.1, 20.0)
        self._gauss_sigma.setSingleStep(0.1)
        self._gauss_sigma.setValue(1.0)
        r2.addWidget(self._gauss_sigma)
        sl.addLayout(r2)

        btn_avg   = QPushButton("▦  Average Filter")
        btn_gauss = QPushButton("◉  Gaussian Filter")
        btn_avg  .clicked.connect(self._emit_average)
        btn_gauss.clicked.connect(self._emit_gaussian)
        sl.addWidget(btn_avg)
        sl.addWidget(btn_gauss)
        return g

    def _build_edge_group(self) -> QGroupBox:
        g  = QGroupBox("Edge Detection")
        el = QVBoxLayout(g)
        el.setSpacing(3)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Operator:"))
        self._edge_op = QComboBox()
        self._edge_op.addItems(["Sobel", "Prewitt"])
        r1.addWidget(self._edge_op)
        el.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Show:"))
        self._edge_component = QComboBox()
        self._edge_component.addItems(["Magnitude", "Horizontal (Gx)", "Vertical (Gy)"])
        r2.addWidget(self._edge_component)
        el.addLayout(r2)

        btn = QPushButton("⟁  Detect Edges")
        btn.clicked.connect(lambda: self.apply_edge.emit(
            self._edge_op.currentText(),
            self._edge_component.currentText()
        ))
        el.addWidget(btn)
        return g

    def _build_median_group(self) -> QGroupBox:
        g  = QGroupBox("Median Filter  (Non-linear)")
        ml = QVBoxLayout(g)
        ml.setSpacing(3)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Kernel:"))
        self._median_kernel = QComboBox()
        self._median_kernel.addItems(["3×3", "5×5", "7×7"])
        r1.addWidget(self._median_kernel)
        ml.addLayout(r1)

        btn = QPushButton("⊡  Apply Median")
        btn.clicked.connect(self._emit_median)
        ml.addWidget(btn)
        return g

    def _build_histeq_group(self) -> QGroupBox:
        g  = QGroupBox("Local Histogram Equalization")
        hl = QVBoxLayout(g)
        hl.setSpacing(3)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Block:"))
        self._block_size = QComboBox()
        self._block_size.addItems(["8×8", "16×16", "32×32", "64×64"])
        r1.addWidget(self._block_size)
        hl.addLayout(r1)

        btn = QPushButton("◑  Local Equalize")
        btn.clicked.connect(self._emit_hist_eq)
        hl.addWidget(btn)
        return g

    # ── Signal emitters ───────────────────────────────────────────────────────

    @staticmethod
    def _combo_size(combo: QComboBox) -> int:
        """Parse '3×3' → 3, '11×11' → 11, etc."""
        return int(combo.currentText().split("×")[0])

    def _emit_average(self):
        self.apply_filter.emit("average", {
            "kernel_size": self._combo_size(self._smooth_kernel)
        })

    def _emit_gaussian(self):
        self.apply_filter.emit("gaussian", {
            "kernel_size": self._combo_size(self._smooth_kernel),
            "sigma":       self._gauss_sigma.value(),
        })

    def _emit_median(self):
        self.apply_median.emit(self._combo_size(self._median_kernel))

    def _emit_hist_eq(self):
        self.apply_hist_eq.emit(self._combo_size(self._block_size))