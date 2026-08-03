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


class AllLogsTabWidget(QtWidgets.QWidget):
    """Widget de aba para exibir logs consolidados de toda a aplicação (raiz 'OpenCMF')."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        self.text_edit = QtWidgets.QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QtGui.QFont("Consolas", 10))
        layout.addWidget(self.text_edit)

        self.handler = QtLogHandler()
        self.handler.log_emitted.connect(self.append_log)

        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(name)s] - (%(filename)s:%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.handler.setFormatter(formatter)

        # Captura todos os logs a partir do root "OpenCMF" propagados
        root_logger = logging.getLogger("OpenCMF")
        root_logger.addHandler(self.handler)
        root_logger.setLevel(logging.DEBUG)

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
        self.resize(950, 650)

        main_layout = QtWidgets.QVBoxLayout(self)

        # Tab Widget Principal
        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Adicionando a aba de Todos os Logs primeiro para acesso rápido
        self.tab_all = AllLogsTabWidget()

        # Abas individuais baseadas nos loggers do sistema (incluindo Patient após Home Page)
        self.tab_main = LogTabWidget("OpenCMF.Main")
        self.tab_home = LogTabWidget("OpenCMF.HomePage")
        self.tab_patient = LogTabWidget("OpenCMF.Patient.Debug")
        self.tab_workspace = LogTabWidget("OpenCMF.Workspace.Debug")
        self.tab_containers = LogTabWidget("OpenCMF.Containers.Debug")
        self.tab_module = LogTabWidget("OpenCMF.Module.Debug")
        self.tab_components = LogTabWidget("OpenCMF.Components.Debug")
        self.tab_scene = LogTabWidget("OpenCMF.Scene.Debug")

        self.tab_widget.addTab(self.tab_all, tr("logs.tab_all", "All Logs"))
        self.tab_widget.addTab(self.tab_main, tr("logs.tab_main", "Main"))
        self.tab_widget.addTab(self.tab_home, tr("logs.tab_home", "Home Page"))
        self.tab_widget.addTab(self.tab_patient, tr("logs.tab_patient", "Patient"))
        self.tab_widget.addTab(self.tab_workspace, tr("configs.workspace", "Workspace"))
        self.tab_widget.addTab(self.tab_containers, tr("logs.tab_containers", "Containers"))
        self.tab_widget.addTab(self.tab_module, tr("logs.tab_module", "Module"))
        self.tab_widget.addTab(self.tab_components, tr("logs.tab_components", "Components"))
        self.tab_widget.addTab(self.tab_scene, tr("logs.tab_scene", "Scene"))

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

    # Logs de teste atualizados
    logging.getLogger("OpenCMF.Main").info("Log de teste na aba Main.")
    logging.getLogger("OpenCMF.HomePage").info("Log de teste na aba Home Page.")
    logging.getLogger("OpenCMF.Patient.Debug").info("Log de teste na aba Patient.")
    logging.getLogger("OpenCMF.Containers.Debug").info("Log de teste na aba Containers.")
    logging.getLogger("OpenCMF.Workspace.Debug").info("Log de teste na aba Workspace.")
    logging.getLogger("OpenCMF.Module.Debug").info("Log de teste na aba Module.")
    logging.getLogger("OpenCMF.Components.Debug").info("Log de teste na aba Components.")
    logging.getLogger("OpenCMF.Scene.Debug").info("Log de teste na aba Scene.")

    sys.exit(app.exec())