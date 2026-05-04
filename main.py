
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
