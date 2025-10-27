from PyQt5.QtWidgets import QApplication
import sys

def get_app():
    import ctypes
    from PyQt5.QtWidgets import QApplication
    import sys

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"mbsistema.unique.id.v1")
    except Exception:
        pass

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMessageBox, QDialog, QInputDialog {
            background-color: #ffffff;
            color: #000000;
            border-radius: 8px;
        }
        QPushButton {
            background-color: #004766;
            color: white;
            border: 1px solid #003555;
            border-radius: 6px;
            padding: 6px 12px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #005580;
        }
        /* ESTILO PARA O CAMPO DE VALOR DO INPUT DIALOG */
        QInputDialog QLineEdit,
        QInputDialog QAbstractSpinBox,
        QInputDialog QDoubleSpinBox,
        QInputDialog QSpinBox,
        QDialog QLineEdit,
        QDialog QAbstractSpinBox,
        QDialog QDoubleSpinBox,
        QDialog QSpinBox {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #c0d9ec !important;
            border-radius: 4px !important;
            padding: 2px !important;
        }
    """)
    return app