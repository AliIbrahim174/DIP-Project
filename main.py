"""
main.py
=======
MedVision Workbench — entry point.

Usage
-----
    python main.py

Project structure
-----------------
    main.py           ← run this
    main_window.py    ← MainWindow (layout, menus, signal wiring)
    sidebar.py        ← ToolsSidebar (all filter/zoom controls)
    panels.py         ← MetadataPanel + PipelinePanel
    widgets.py        ← ImageCanvas + HistogramWidget
    worker.py         ← ProcessingWorker (background QThread)
    styles.py         ← all Qt stylesheets and colour tokens
    image_processor.py← all DSP algorithms (from scratch)
    image_io.py       ← DICOM / JPEG / BMP / PNG I/O
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore    import Qt

from app.gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MedVision Workbench")
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
