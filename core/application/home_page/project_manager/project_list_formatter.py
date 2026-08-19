from __future__ import annotations

from PySide6 import QtCore, QtWidgets

# Localization
from core.settings.localization.translator import tr


class ProjectItemWidget(QtWidgets.QWidget):
    """Widget para o modo de exibição em Lista."""

    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(10)

        pacient = self.data.get("paciente", {})
        nome = pacient.get("nome", tr("home.unknown_patient", "Paciente Desconhecido"))
        sex = pacient.get("sexo", "N/A")
        birth = pacient.get("nascimento")
        creation = self.data.get("created_at", 0)

        # Usando chaves traduzidas ou formatadores baseados na estrutura atual
        info_extra = f"{tr('patient.label_gender', 'Sexo')} {sex}"
        idade = self._calculate_age(birth, creation)
        if idade is not None:
            info_extra += f" | {tr('patient.age', 'Idade')}: {idade} anos"

        lbl_nome = QtWidgets.QLabel(f"<b>{nome}</b> - {info_extra}")

        data_str = QtCore.QDateTime.fromSecsSinceEpoch(int(creation)).toString(
            "dd/MM/yy HH:mm"
        )
        lbl_data = QtWidgets.QLabel(data_str)

        layout.addWidget(lbl_nome)
        layout.addStretch()
        layout.addWidget(lbl_data)

    def _calculate_age(self, nascimento_str, criacao_ts):
        if not nascimento_str:
            return None
        date_birth = QtCore.QDate.fromString(nascimento_str, "yyyy-MM-dd")
        dt_criacao = QtCore.QDateTime.fromSecsSinceEpoch(int(criacao_ts)).date()
        if not date_birth.isValid() or date_birth == dt_criacao:
            return None
        age = dt_criacao.year() - date_birth.year()
        if (dt_criacao.month(), dt_criacao.day()) < (
            date_birth.month(),
            date_birth.day(),
        ):
            age -= 1
        return age


class ProjectCardWidget(QtWidgets.QFrame):
    clicked = QtCore.Signal(str)

    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self.setFixedSize(100, 120)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        layout = QtWidgets.QVBoxLayout(self)
        nome = data.get("paciente", {}).get("nome", tr("home.unknown_patient", "Paciente Desconhecido"))
        lbl_nome = QtWidgets.QLabel(nome)
        lbl_nome.setWordWrap(True)
        lbl_nome.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(lbl_nome)
        layout.addStretch()

    def mousePressEvent(self, event):
        path = self.data.get("_path")
        if path:
            self.clicked.emit(path)


def format_and_add_to_list(list_widget: QtWidgets.QListWidget, data: dict):
    path = data.get("_path")
    item = QtWidgets.QListWidgetItem(list_widget)
    widget = ProjectItemWidget(data)
    item.setSizeHint(QtCore.QSize(widget.sizeHint().width(), 28))
    item.setData(QtCore.Qt.UserRole, path)
    list_widget.addItem(item)
    list_widget.setItemWidget(item, widget)
    return item


def create_project_card(data: dict):
    return ProjectCardWidget(data)