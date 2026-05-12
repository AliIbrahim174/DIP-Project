from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout, 
    QPushButton, QGridLayout, QSizePolicy, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import numpy as np
from .widgets import HistogramWidget, ImageCanvas


class ROIStatsDialog(QDialog):
    """Dialog showing ROI statistics, preview, and operations."""
    
    def __init__(self, stats_dict: dict, parent=None, on_apply_callback=None):
        """
        Args:
            stats_dict: Dict from compute_roi_stats() with keys:
                - roi_array, hist, mean, std, min, max, median, entropy, area
            parent: Parent widget
            on_apply_callback: Callable(operation_name) for operation buttons
        """
        super().__init__(parent)
        self.setWindowTitle("ROI — Local Statistics & Operations")
        self.setMinimumSize(600, 500)
        self.stats = stats_dict
        self.on_apply_callback = on_apply_callback

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # ========== ROI Preview ==========
        preview_group = QGroupBox("ROI Region Preview")
        preview_layout = QHBoxLayout(preview_group)
        
        self._preview_label = QLabel()
        self._preview_label.setMinimumSize(150, 150)
        self._preview_label.setStyleSheet("background-color: #222; border: 1px solid #555;")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._render_preview()
        preview_layout.addWidget(self._preview_label)
        layout.addWidget(preview_group)

        # ========== Statistics Grid ==========
        stats_group = QGroupBox("Pixel Intensity Statistics")
        stats_grid = QGridLayout(stats_group)
        stats_grid.setSpacing(8)

        stats_labels = [
            ("Mean", f"{stats_dict['mean']:.2f}"),
            ("Std Dev", f"{stats_dict['std']:.2f}"),
            ("Min", f"{stats_dict['min']}"),
            ("Max", f"{stats_dict['max']}"),
            ("Median", f"{stats_dict['median']}"),
            ("Entropy", f"{stats_dict['entropy']:.3f}"),
            ("Pixels", f"{stats_dict['area']:,}"),
        ]

        for row, (label_text, value_text) in enumerate(stats_labels):
            label = QLabel(label_text + ":")
            label.setStyleSheet("font-weight: 600;")
            value = QLabel(value_text)
            value.setStyleSheet("color: #0f8;")
            stats_grid.addWidget(label, row, 0, alignment=Qt.AlignmentFlag.AlignRight)
            stats_grid.addWidget(value, row, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(stats_group)

        # ========== Histogram ==========
        hist_group = QGroupBox("ROI Histogram")
        hist_layout = QVBoxLayout(hist_group)
        self._hist_widget = HistogramWidget()
        self._hist_widget.set_hist(stats_dict['hist'])
        hist_layout.addWidget(self._hist_widget)
        layout.addWidget(hist_group)

        # ========== Operations Buttons ==========
        ops_group = QGroupBox("Local Operations")
        ops_layout = QHBoxLayout(ops_group)

        ops = [
            ("Equalize ROI", "equalize_roi"),
            ("Median ROI", "median_roi"),
            ("Extract ROI", "extract_roi"),
        ]

        for label_text, op_id in ops:
            btn = QPushButton(label_text)
            btn.clicked.connect(lambda checked, op=op_id: self._on_operation(op))
            ops_layout.addWidget(btn)

        layout.addWidget(ops_group)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _render_preview(self):
        """Render ROI region as preview image."""
        roi = self.stats['roi_array']
        h, w = roi.shape[:2]

        # Scale if too small
        scale = max(1, 150 // max(h, w))
        roi_scaled = np.repeat(np.repeat(roi, scale, axis=0), scale, axis=1)

        # Convert to QPixmap
        roi_u8 = (roi_scaled * 255 // 255).astype(np.uint8) if roi.max() <= 1 else roi_scaled.astype(np.uint8)
        h_scaled, w_scaled = roi_u8.shape
        image = QImage(roi_u8.data, w_scaled, h_scaled, w_scaled, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(image)
        self._preview_label.setPixmap(pixmap)

    def _on_operation(self, op_id: str):
        """Handle operation button clicks."""
        if self.on_apply_callback:
            self.on_apply_callback(op_id, self.stats)
        self.accept()