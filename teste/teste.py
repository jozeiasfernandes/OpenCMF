import sys
from PySide6 import QtWidgets, QtCore


class DemoLayout(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCMF - Demo Layouts")
        self.resize(900, 600)

        # Widget Principal
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        layout_v = QtWidgets.QVBoxLayout(main_widget)

        # Seletor
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(["Opção 1: Accordion", "Opção 2: Abas (Tabs)", "Opção 3: Duas Sidebars"])
        self.combo.currentIndexChanged.connect(self.mudar_layout)
        layout_v.addWidget(QtWidgets.QLabel("Selecione o estilo de interface:"))
        layout_v.addWidget(self.combo)

        # Área de Conteúdo (Stack)
        self.stack = QtWidgets.QStackedWidget()
        layout_v.addWidget(self.stack)

        self.stack.addWidget(self.layout_accordion())
        self.stack.addWidget(self.layout_tabs())
        self.stack.addWidget(self.layout_multiplo())

    def dummy_3d(self, cor="#1a1a1a"):
        label = QtWidgets.QLabel("Área de Visualização 3D")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet(f"background-color: {cor}; border-radius: 10px; color: gray; font-weight: bold;")
        return label

    def layout_accordion(self):
        w = QtWidgets.QWidget()
        l = QtWidgets.QHBoxLayout(w)
        l.addWidget(self.dummy_3d(), stretch=1)
        sidebar = QtWidgets.QVBoxLayout()
        for t in ["Objetos", "Cortes", "Exportar"]:
            btn = QtWidgets.QPushButton(t)
            btn.setMinimumHeight(40)
            sidebar.addWidget(btn)
        sidebar.addStretch()
        l.addLayout(sidebar)
        return w

    def layout_tabs(self):
        w = QtWidgets.QWidget()
        l = QtWidgets.QHBoxLayout(w)
        l.addWidget(self.dummy_3d("#151525"), stretch=1)
        tabs = QtWidgets.QTabWidget()
        tabs.setTabPosition(QtWidgets.QTabWidget.East)
        tabs.addTab(QtWidgets.QLabel("Ferramentas A"), "🛠️")
        tabs.addTab(QtWidgets.QLabel("Ferramentas B"), "📏")
        l.addWidget(tabs)
        return w

    def layout_multiplo(self):
        w = QtWidgets.QWidget()
        l = QtWidgets.QHBoxLayout(w)

        # Esquerda
        lista = QtWidgets.QListWidget()
        lista.addItems(["Mandíbula.stl", "Crânio.stl"])
        lista.setFixedWidth(150)

        # Direita
        prop = QtWidgets.QVBoxLayout()
        prop.addWidget(QtWidgets.QLabel("Propriedades"))
        prop.addWidget(QtWidgets.QSlider(QtCore.Qt.Horizontal))
        prop.addStretch()

        l.addWidget(lista)
        l.addWidget(self.dummy_3d("#201010"), stretch=1)
        l.addLayout(prop)
        return w

    def mudar_layout(self, i):
        self.stack.setCurrentIndex(i)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DemoLayout()
    win.show()
    sys.exit(app.exec())