import logging
from PySide6 import QtWidgets, QtCore, QtGui

from core.settings.localization.translator import tr


class QtLogHandler(logging.Handler, QtCore.QObject):
    """Handler customizado para enviar logs do Python via Qt Signals para a UI."""
    log_emitted = QtCore.Signal(str)

    def __init__(self):
        logging.Handler.__init__(self)
        QtCore.QObject.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        self.log_emitted.emit(msg)


class LogTabWidget(QtWidgets.QWidget):
    """Widget de aba individual contendo um visualizador de texto para logs."""

    def __init__(self, logger_name: str, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        self.text_edit = QtWidgets.QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QtGui.QFont("Consolas", 10))
        layout.addWidget(self.text_edit)

        # Configurando o Handler para este logger específico
        self.handler = QtLogHandler()
        self.handler.log_emitted.connect(self.append_log)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(name)s] - (%(filename)s:%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.handler.setFormatter(formatter)

        target_logger = logging.getLogger(logger_name)
        target_logger.addHandler(self.handler)
        target_logger.setLevel(logging.DEBUG)

    @QtCore.Slot(str)
    def append_log(self, message: str):
        self.text_edit.appendPlainText(message)
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class LogMonitorWindow(QtWidgets.QDialog):
    """Janela principal do Monitor de Logs contendo todas as abas com suporte a traduções."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("logs.monitor_title", "System Log Monitor - OpenCMF"))
        self.resize(900, 600)

        main_layout = QtWidgets.QVBoxLayout(self)

        # Tab Widget Principal
        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Adicionando as Abas baseadas nos loggers do sistema e chaves de tradução
        self.tab_main = LogTabWidget("OpenCMF.Main")
        self.tab_home = LogTabWidget("OpenCMF.HomePage")
        self.tab_workspace = LogTabWidget("OpenCMF.Workspace.Debug")
        self.tab_containers = LogTabWidget("OpenCMF.Containers.Debug")
        self.tab_module = LogTabWidget("OpenCMF.Module.Debug")

        self.tab_widget.addTab(self.tab_main, tr("logs.tab_main", "Main"))
        self.tab_widget.addTab(self.tab_home, tr("logs.tab_home", "Home Page"))
        self.tab_widget.addTab(self.tab_workspace, tr("configs.workspace", "Workspace"))
        self.tab_widget.addTab(self.tab_containers, tr("logs.tab_containers", "Containers"))
        self.tab_widget.addTab(self.tab_module, tr("logs.tab_module", "Module"))

        # Botões Inferiores (Copy e Exit traduzidos)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        self.btn_copy = QtWidgets.QPushButton(tr("logs.btn_copy", "Copy"))
        self.btn_copy.clicked.connect(self.copy_current_logs)
        btn_layout.addWidget(self.btn_copy)

        self.btn_exit = QtWidgets.QPushButton(tr("common.close_button", "Exit"))
        self.btn_exit.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_exit)

        main_layout.addLayout(btn_layout)

    def copy_current_logs(self):
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, "text_edit"):
            clipboard = QtGui.QGuiApplication.clipboard()
            clipboard.setText(current_widget.text_edit.toPlainText())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    monitor_window = LogMonitorWindow()
    monitor_window.show()

    # Logs de teste
    logging.getLogger("OpenCMF.Main").info("Log de teste na aba Main.")
    logging.getLogger("OpenCMF.HomePage").info("Log de teste na aba Home Page.")
    logging.getLogger("OpenCMF.Containers.Debug").info("Log de teste na aba Containers.")
    logging.getLogger("OpenCMF.Workspace.Debug").info("Log de teste na aba Workspace.")
    logging.getLogger("OpenCMF.Module.Debug").info("Log de teste na aba Module.")

    sys.exit(app.exec())