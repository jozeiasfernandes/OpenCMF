'''
Fluxo:
* ImportObjectsPanel emite o sinal.
*Controller (ou o componente que coordena a cena) recebe esse sinal.
* Controller abre um QFileDialog para o usuário escolher o arquivo STL/VTI/JPG.
* Controller chama o ObjectManager (que refatoramos antes).

O ObjectManager tem o "poder" de copiar o arquivo para a pasta do paciente e criar a estrutura de pastas.

Quando o arquivo for salvo com sucesso na pasta do paciente pelo ObjectManager, o sistema precisa "dar vida" a esse arquivo na tela. É aqui que a pasta scene entra:

* O SceneObject (que está em core/scene/) é instanciado para representar esse novo objeto.
* O ObjectRegistry (também na pasta de cena) guarda esse objeto para que o sistema saiba que ele existe.
* A VTKActorFactory (que analisamos hoje) pega esse SceneObject e cria o ator 3D para ser exibido na tela.

Resumo Arquitetural:
Camada UI: ImportObjectsPanel

Camada de Lógica: SceneController & ObjectManager

Camada de Dados: SceneObject & ObjectSaver

Camada Gráfica: VTKActorFactory

'''
import sys
from typing import Optional, Callable, List, Tuple
from core.scene.io.importer import ObjectImporter
from core.scene.registry import ObjectRegistry
from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFrame,
    QVBoxLayout, QGridLayout, QApplication, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QPoint, QSize, QEvent
from PySide6.QtGui import QIcon
from settings.localization.translator import tr
from core.scene.rendering.vtk_actor_factory import VTKActorFactory
from list_paths import ICONS_DIR

# Centralização de cores e estilos para fácil manutenção
COLORS = {
    "surfaces": "#b0a8c0",
    "photos": "#c9a7a0",
    "volume": "#bcd4d0",
    "hover": "#ffffff"
}


def get_icon_path(icon_name: str) -> str:
    path = ICONS_DIR / icon_name
    return str(path) if path.exists() else ""


class ImportCard(QPushButton):
    def __init__(self, text: str, category_key: str, icon_name: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(130, 40)

        icon_path = get_icon_path(icon_name)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))

        color = COLORS.get(category_key, "#cccccc")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 4px;
                color: black;
                font-weight: bold;
                border: none;
                font-size: 11px;
                text-align: left;
                padding-left: 10px;
            }}
            QPushButton:hover {{ background-color: {COLORS['hover']}; }}
        """)


class ImportSection(QFrame):
    def __init__(self, title: str, category_key: str, items: List[Tuple[str, str]],
                 callback: Callable[[str, str], None], parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        label = QLabel(title.upper())
        label.setStyleSheet("color: #888; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(label)

        grid = QGridLayout()
        grid.setSpacing(8)

        for i, (name, icon) in enumerate(items):
            btn = ImportCard(name, category_key, icon, self)
            # Usamos o category_key para o sinal ser processável pelo ObjectManager
            btn.clicked.connect(lambda _, n=name, k=category_key: callback(k, n))
            grid.addWidget(btn, i // 4, i % 4)

        layout.addLayout(grid)


class SceneController:
    def __init__(self, importer: ObjectImporter, registry: ObjectRegistry, actor_factory: VTKActorFactory):
        self.importer = importer
        self.registry = registry
        self.actor_factory = actor_factory

    def on_import_requested(self, category: str, subcategory: str):
        # 1. Abrir o seletor de arquivos
        # O filtro pode ser dinâmico baseado na categoria se desejar
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Selecionar Arquivo", "", "Arquivos Suportados (*.stl *.vti *.jpg *.png *.dcm)"
        )

        if file_path:
            # 2. Delegar a cópia física (ObjectManager/Importer)
            scene_obj = self.importer.import_external_file(file_path, category)

            if scene_obj:
                # 3. Registrar o objeto (SceneRegistry)
                self.registry.add(scene_obj)

                # 4. Renderizar (VTKActorFactory)
                self.actor_factory.create_actor(scene_obj)


class ImportObjectsPanel(QFrame):
    # Sinal emite (categoria_interna, subcategoria_traduzida)
    importRequested = Signal(str, str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setMinimumWidth(580)
        self.setObjectName("ImportPanel")

        self.setStyleSheet("""
            QFrame#ImportPanel {
                background-color: #2b2b2b;
                border: 1px solid #444;
                border-radius: 6px;
            }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(25)

        self._setup_sections()

    def _setup_sections(self) -> None:
        sections = [
            (
                tr("import.secao.superficies", "Superfícies"),
                "surfaces",
                [
                    (tr("import.superficies.cranio", "Crânio"), "cranio.svg"),
                    (tr("import.superficies.maxila", "Maxila"), "maxilla.svg"),
                    (tr("import.superficies.mandibula", "Mandíbula"), "mandible.svg"),
                    (tr("import.superficies.pele", "Pele"), "face.svg"),
                    (tr("import.superficies.outros", "Outros"), "stl.svg")
                ]
            ),
            (
                tr("import.secao.fotografias", "Fotografias"),
                "photos",
                [
                    (tr("import.fotografias.frente", "Frente"), "fronte.svg"),
                    (tr("import.fotografias.perfil", "Perfil"), "perfil.svg"),
                    (tr("import.fotografias.intrabucal", "Intrabucal"), "photo.svg")
                ]
            ),
            (
                tr("import.secao.volume", "Volume"),
                "volume",
                [(tr("import.volumes.volume_vti", "Volume .vti"), "vti.svg")]
            )
        ]

        for title, key, items in sections:
            sec = ImportSection(title, key, items, self._on_item_clicked, self)
            self.main_layout.addWidget(sec)

    def _on_item_clicked(self, category_key: str, subcategory: str) -> None:
        self.importRequested.emit(category_key, subcategory)
        self.hide()

    def show_under(self, widget: QWidget) -> None:
        point = widget.mapToGlobal(QPoint(0, widget.height() + 5))
        self.move(point)
        self.show()
        self.setFocus()

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate:
            self.hide()
        return super().event(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_window = QWidget()
    test_window.setMinimumSize(800, 600)
    test_window.setStyleSheet("background-color: #1e1e1e;")

    btn = QPushButton(tr("import.btn.import_objects", "Import Objects"), test_window)
    btn.setFixedSize(130, 30)
    btn.move(50, 50)
    btn.setStyleSheet("background-color: #444; color: white;")

    panel = ImportObjectsPanel(test_window)
    btn.clicked.connect(lambda: panel.show_under(btn))
    panel.importRequested.connect(lambda cat, sub: print(f"Importando: {cat} -> {sub}"))

    test_window.show()
    sys.exit(app.exec())