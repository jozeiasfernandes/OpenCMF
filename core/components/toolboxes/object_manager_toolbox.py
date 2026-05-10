import sys
import json
import logging
import random
import uuid
from pathlib import Path
from typing import Dict, Optional

from PySide6 import QtWidgets, QtCore, QtGui

import vtkmodules.all as vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from core.imports.models_import import ObjectProperties

logger = logging.getLogger("ObjectManagerWidget")

_TIPO_CAT = {
    "surfaces": "Superfícies",
    "photos": "Fotografias",
    "volume": "Volume",
    "others": "Outros",
}

_CAT_TIPO = {v: k for k, v in _TIPO_CAT.items()}


class ObjetoManagerWidget(QtWidgets.QWidget):
    objetoToggled = QtCore.Signal(str, bool)
    opacityChanged = QtCore.Signal(str, float)
    colorChanged = QtCore.Signal(str, QtGui.QColor)
    deleteRequested = QtCore.Signal(str)
    nomeAlterado = QtCore.Signal(str, str)
    objetoSelecionado = QtCore.Signal(str)

    def __init__(self, parent=None, patient_path: Optional[str] = None):
        super().__init__(parent)

        self.object_properties: Dict[str, ObjectProperties] = {}
        self._nome_para_id: Dict[str, str] = {}
        self.cats: Dict[str, QtWidgets.QTreeWidgetItem] = {}

        self.patient_path: Optional[Path] = (
            Path(patient_path) if patient_path else None
        )

        self._is_initializing = True
        self._pending_save_id: Optional[str] = None

        self._save_timer = QtCore.QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(400)
        self._save_timer.timeout.connect(self._flush_save)

        self._setup_ui()

        if self.patient_path:
            self.carregar_objetos_da_pasta()

        self._is_initializing = False

    # ─────────────────────────────────────────────────────────────

    def set_patient_path(self, path: str) -> None:
        self.patient_path = Path(path)
        self.carregar_objetos_da_pasta()

    def get_object_properties(
        self,
        identificador: str
    ) -> Optional[ObjectProperties]:

        return (
            self.object_properties.get(identificador)
            or self.object_properties.get(
                self._nome_para_id.get(identificador, "")
            )
        )

    # ─────────────────────────────────────────────────────────────

    def carregar_objetos_da_pasta(self) -> None:
        if not self.patient_path or not self.patient_path.exists():
            logger.warning(f"Caminho não existe: {self.patient_path}")
            return

        self.tree_widget.blockSignals(True)

        self.tree_widget.clear()
        self.cats.clear()
        self._nome_para_id.clear()
        self.object_properties.clear()

        count = 0

        for jf in self.patient_path.rglob("*.json"):
            if "project" in jf.parts:
                continue

            try:
                props = ObjectProperties.from_json(
                    json.loads(
                        jf.read_text(encoding="utf-8")
                    )
                )

                self.object_properties[props.id] = props

                self._adicionar_item_arvore(
                    props,
                    _TIPO_CAT.get(props.type, "Outros")
                )

                count += 1

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError
            ) as e:
                logger.warning(f"Erro ao carregar {jf}: {e}")

        self.tree_widget.blockSignals(False)

        logger.info(
            f"{count} objeto(s) carregados — {self.patient_path}"
        )

    # ─────────────────────────────────────────────────────────────

    def adicionar_objeto_lista(
        self,
        nome_ou_props=None,
        categoria="Superfícies",
        cor=None,
        objeto_id=None,
        props=None
    ) -> None:

        if props is None:
            props = (
                nome_ou_props
                if isinstance(nome_ou_props, ObjectProperties)
                else None
            )

        if props is None:
            oid = objeto_id or str(uuid.uuid4())

            props = (
                self.object_properties.get(oid)
                or ObjectProperties(
                    id=oid,
                    name=nome_ou_props or "",
                    type=_CAT_TIPO.get(categoria, "others")
                )
            )

            if cor:
                props.render["color"] = list(cor)

            if nome_ou_props:
                props.name = nome_ou_props

        self.object_properties[props.id] = props

        self._adicionar_item_arvore(props, categoria)

    # ─────────────────────────────────────────────────────────────

    def salvar_alteracao_objeto(self, objeto_id: str) -> None:
        props = self.object_properties.get(objeto_id)

        if (
            not props
            or not self.patient_path
            or not props.file_path
        ):
            return

        json_path = (
            self.patient_path / props.file_path
        ).with_suffix(".json")

        try:
            json_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            json_path.write_text(
                json.dumps(
                    props.to_json(),
                    indent=4,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

            logger.debug(f"Salvo: {props.name}")

        except Exception as e:
            logger.error(f"Erro ao salvar {props.name}: {e}")

    def _flush_save(self) -> None:
        if self._pending_save_id:
            self.salvar_alteracao_objeto(
                self._pending_save_id
            )

            self._pending_save_id = None

    # ─────────────────────────────────────────────────────────────

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.tree_widget = QtWidgets.QTreeWidget()

        self.tree_widget.setHeaderLabels([
            "Lista de Objetos",
            "Opacidade",
            "Cor"
        ])

        self.tree_widget.setIndentation(12)
        self.tree_widget.setUniformRowHeights(True)

        self.tree_widget.setIconSize(
            QtCore.QSize(12, 12)
        )

        self.tree_widget.setContextMenuPolicy(
            QtCore.Qt.CustomContextMenu
        )

        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                padding: 0px;
                margin: 0px;
            }

            QTreeView::item {
                padding-top: 1px;
                padding-bottom: 1px;
            }

            QHeaderView::section {
                padding: 2px;
            }
        """)

        h = self.tree_widget.header()

        h.setStretchLastSection(False)

        h.setMinimumSectionSize(20)

        h.setSectionResizeMode(
            0,
            QtWidgets.QHeaderView.Stretch
        )

        h.setSectionResizeMode(
            1,
            QtWidgets.QHeaderView.Fixed
        )

        h.setSectionResizeMode(
            2,
            QtWidgets.QHeaderView.Fixed
        )

        self.tree_widget.setColumnWidth(1, 90)
        self.tree_widget.setColumnWidth(2, 32)

        self.tree_widget.itemClicked.connect(
            self._on_item_clicked
        )

        self.tree_widget.itemChanged.connect(
            self._handle_item_changed
        )

        self.tree_widget.doubleClicked.connect(
            self._on_double_clicked
        )

        self.tree_widget.customContextMenuRequested.connect(
            self._show_context_menu
        )

        layout.addWidget(self.tree_widget)

    # ─────────────────────────────────────────────────────────────

    def _get_or_create_category(
        self,
        name: str
    ) -> QtWidgets.QTreeWidgetItem:

        if name not in self.cats:
            it = QtWidgets.QTreeWidgetItem(
                self.tree_widget
            )

            it.setText(0, name)
            it.setExpanded(True)

            it.setBackground(
                0,
                QtGui.QColor(240, 240, 240, 40)
            )

            it.setFirstColumnSpanned(True)

            f = it.font(0)
            f.setBold(True)

            it.setFont(0, f)

            self.cats[name] = it

        return self.cats[name]

    # ─────────────────────────────────────────────────────────────

    def _adicionar_item_arvore(
        self,
        props: ObjectProperties,
        categoria: str
    ) -> None:

        self._nome_para_id[props.name] = props.id

        item = QtWidgets.QTreeWidgetItem(
            self._get_or_create_category(categoria)
        )

        item.setText(0, props.name)

        item.setFlags(
            item.flags()
            | QtCore.Qt.ItemIsUserCheckable
        )

        item.setCheckState(
            0,
            QtCore.Qt.Checked
            if props.visible
            else QtCore.Qt.Unchecked
        )

        item.setData(
            0,
            QtCore.Qt.UserRole,
            props.id
        )

        slider = QtWidgets.QSlider(
            QtCore.Qt.Horizontal
        )

        slider.setRange(0, 100)

        slider.setValue(
            int(props.opacity * 100)
        )

        slider.setMaximumHeight(14)

        slider.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )

        slider.valueChanged.connect(
            lambda v, oid=props.id:
            self._on_opacity_changed(oid, v)
        )

        self.tree_widget.setItemWidget(
            item,
            1,
            slider
        )

        btn = QtWidgets.QPushButton()

        btn.setMaximumSize(14, 14)

        btn.setContentsMargins(0, 0, 0, 0)

        btn.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed,
            QtWidgets.QSizePolicy.Fixed
        )

        c = props.render.get(
            "color",
            [0.3, 0.6, 1.0]
        )

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color:
                    {QtGui.QColor.fromRgbF(c[0], c[1], c[2]).name()};
                border-radius: 7px;
                border: 1px solid #888;
                padding: 0px;
                margin: 0px;
            }}
        """)

        btn.clicked.connect(
            lambda _, oid=props.id, b=btn:
            self._pick_color(oid, b)
        )

        self.tree_widget.setItemWidget(
            item,
            2,
            btn
        )

    # ─────────────────────────────────────────────────────────────

    def _on_item_clicked(self, item, _col):
        if item.parent() is not None:
            oid = item.data(
                0,
                QtCore.Qt.UserRole
            )

            if oid:
                self.objetoSelecionado.emit(oid)

    def _handle_item_changed(self, item, column):
        if column != 0 or item.parent() is None:
            return

        oid = item.data(
            0,
            QtCore.Qt.UserRole
        )

        if not oid:
            return

        visivel = (
            item.checkState(0)
            == QtCore.Qt.Checked
        )

        if oid in self.object_properties:
            self.object_properties[oid].visible = visivel

            self.salvar_alteracao_objeto(oid)

        if not self._is_initializing:
            self.objetoToggled.emit(oid, visivel)

    def _on_double_clicked(self, index):
        item = self.tree_widget.itemFromIndex(index)

        if not item or item.parent() is None:
            return

        nome_original = item.text(0)

        oid = item.data(
            0,
            QtCore.Qt.UserRole
        )

        novo, ok = QtWidgets.QInputDialog.getText(
            self,
            "Renomear",
            f"Nome atual: {nome_original}",
            QtWidgets.QLineEdit.Normal,
            nome_original
        )

        if ok and novo and novo != nome_original:
            self.tree_widget.blockSignals(True)

            item.setText(0, novo)

            self.tree_widget.blockSignals(False)

            self._nome_para_id.pop(
                nome_original,
                None
            )

            self._nome_para_id[novo] = oid

            if oid in self.object_properties:
                self.object_properties[oid].name = novo

                self.salvar_alteracao_objeto(oid)

            self.nomeAlterado.emit(oid, novo)

    def _show_context_menu(self, pos):
        item = self.tree_widget.itemAt(pos)

        if not item or item.parent() is None:
            return

        menu = QtWidgets.QMenu()

        action = menu.addAction("Excluir")

        if (
            action
            == menu.exec(
                self.tree_widget.viewport().mapToGlobal(pos)
            )
        ):
            oid = item.data(
                0,
                QtCore.Qt.UserRole
            )

            self._nome_para_id.pop(
                item.text(0),
                None
            )

            self.object_properties.pop(
                oid,
                None
            )

            cat = item.parent()

            cat.removeChild(item)

            if cat.childCount() == 0:
                self.cats.pop(
                    cat.text(0),
                    None
                )

                self.tree_widget.invisibleRootItem().removeChild(cat)

            self.deleteRequested.emit(oid)

    def _on_opacity_changed(
        self,
        oid: str,
        value: int
    ) -> None:

        if oid in self.object_properties:
            self.object_properties[oid].opacity = value / 100.0

            self._pending_save_id = oid

            self._save_timer.start()

        if not self._is_initializing:
            self.opacityChanged.emit(
                oid,
                value / 100.0
            )

    def _pick_color(
        self,
        oid: str,
        btn: QtWidgets.QPushButton
    ) -> None:

        color = QtWidgets.QColorDialog.getColor()

        if not color.isValid():
            return

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border-radius: 7px;
                border: 1px solid #888;
                padding: 0px;
                margin: 0px;
            }}
        """)

        if oid in self.object_properties:
            self.object_properties[oid].render["color"] = [
                color.redF(),
                color.greenF(),
                color.blueF()
            ]

            self.salvar_alteracao_objeto(oid)

        self.colorChanged.emit(oid, color)


# ─────────────────────────────────────────────────────────────────────────────


class Component(QtWidgets.QWidget):
    toolbox_name = "Lista de Objetos"

    def __init__(self, modulo=None):
        super().__init__()

        layout = QtWidgets.QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.manager = ObjetoManagerWidget()

        layout.addWidget(self.manager)

        if modulo:
            for sinal, handler in [
                ("objetoToggled", "on_objeto_toggled"),
                ("opacityChanged", "on_opacity_changed"),
                ("colorChanged", "on_color_changed"),
                ("deleteRequested", "on_delete_requested"),
                ("nomeAlterado", "on_nome_alterado"),
                ("objetoSelecionado", "on_objeto_selecionado"),
            ]:
                if hasattr(modulo, handler):
                    getattr(
                        self.manager,
                        sinal
                    ).connect(
                        getattr(modulo, handler)
                    )

            pasta = getattr(
                modulo,
                "pasta_paciente",
                None
            )

            if pasta:
                self.manager.set_patient_path(pasta)

    def set_patient_path(self, path: str) -> None:
        self.manager.set_patient_path(path)


# ─────────────────────────────────────────────────────────────────────────────


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "OpenCMF - Visualizador de Objetos"
        )

        self.resize(1200, 800)

        self.pasta_paciente = Path(
            "./teste_registro_standalone/STL"
        )

        self.pasta_paciente.mkdir(
            parents=True,
            exist_ok=True
        )

        self.atores: Dict[str, vtk.vtkActor] = {}

        self.vtk_widget = QVTKRenderWindowInteractor(self)

        self.renderer = vtk.vtkRenderer()

        self.vtk_widget.GetRenderWindow().AddRenderer(
            self.renderer
        )

        self.renderer.SetBackground(
            0.05,
            0.05,
            0.1
        )

        self.vtk_widget.Initialize()

        self.manager_widget = ObjetoManagerWidget()

        toolbox = QtWidgets.QToolBox()

        toolbox.addItem(
            self.manager_widget,
            "Gerenciador de Objetos"
        )

        self.setCentralWidget(QtWidgets.QWidget())

        layout = QtWidgets.QHBoxLayout(
            self.centralWidget()
        )

        layout.setContentsMargins(2, 2, 2, 2)

        layout.addWidget(toolbox, 1)
        layout.addWidget(self.vtk_widget, 4)

        m = self.manager_widget

        m.objetoToggled.connect(
            lambda oid, v:
            (
                self.atores[oid].SetVisibility(v),
                self._render()
            )
            if oid in self.atores else None
        )

        m.opacityChanged.connect(
            lambda oid, v:
            (
                self.atores[oid]
                .GetProperty()
                .SetOpacity(v),

                self._render()
            )
            if oid in self.atores else None
        )

        m.colorChanged.connect(
            lambda oid, c:
            (
                self.atores[oid]
                .GetProperty()
                .SetColor(
                    c.redF(),
                    c.greenF(),
                    c.blueF()
                ),

                self._render()
            )
            if oid in self.atores else None
        )

        m.deleteRequested.connect(
            self._remove_actor
        )

        for fp in (
            list(self.pasta_paciente.glob("*.stl"))
            + list(self.pasta_paciente.glob("*.obj"))
        ):
            self._load(fp)

        self.renderer.ResetCamera()

        self._render()

    def _render(self):
        self.vtk_widget.GetRenderWindow().Render()

    def _load(self, fp: Path):
        ext = fp.suffix.lower()

        reader = (
            vtk.vtkSTLReader()
            if ext == ".stl"
            else vtk.vtkOBJReader()
        )

        reader.SetFileName(str(fp))
        reader.Update()

        mapper = vtk.vtkPolyDataMapper()

        mapper.SetInputConnection(
            reader.GetOutputPort()
        )

        actor = vtk.vtkActor()

        actor.SetMapper(mapper)

        color = [
            random.random()
            for _ in range(3)
        ]

        actor.GetProperty().SetColor(color)

        self.renderer.AddActor(actor)

        props = ObjectProperties(
            name=fp.stem,
            type="surfaces",
            file_path=str(
                fp.relative_to(self.pasta_paciente)
            ),
            format=ext.lstrip(".")
        )

        props.render["color"] = color

        self.atores[props.id] = actor

        self.manager_widget.adicionar_objeto_lista(
            props,
            "Arquivos Locais"
        )

    def _remove_actor(self, oid: str):
        actor = self.atores.pop(oid, None)

        if actor:
            self.renderer.RemoveActor(actor)

            self._render()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")

    window = MainWindow()

    window.show()

    sys.exit(app.exec())