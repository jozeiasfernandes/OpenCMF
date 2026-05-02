from PySide6 import QtWidgets, QtCore


class ProjectItemWidget(QtWidgets.QWidget):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(10)

        paciente = self.data.get("paciente", {})
        nome = paciente.get("nome", "Sem Nome")
        sexo = paciente.get("sexo", "N/A")
        nascimento = paciente.get("nascimento")
        criacao = self.data.get("created_at", 0)

        info_extra = f"Sexo: {sexo}"

        idade = self._calcular_idade(nascimento, criacao)
        if idade is not None:
            info_extra += f" | Idade: {idade} anos"

        lbl_nome = QtWidgets.QLabel(
            f"<b>{nome}</b> <span style='color: #888; font-size: 10px;'> - {info_extra}</span>"
        )

        data_str = QtCore.QDateTime.fromSecsSinceEpoch(int(criacao)).toString("dd/MM/yy HH:mm")
        lbl_data = QtWidgets.QLabel(data_str)
        lbl_data.setStyleSheet("color: #555; font-size: 9px;")

        layout.addWidget(lbl_nome)
        layout.addStretch()
        layout.addWidget(lbl_data)

    def _calcular_idade(self, nascimento_str, criacao_ts):
        if not nascimento_str:
            return None

        dt_nascimento = QtCore.QDate.fromString(nascimento_str, "yyyy-MM-dd")
        dt_criacao = QtCore.QDateTime.fromSecsSinceEpoch(int(criacao_ts)).date()

        if not dt_nascimento.isValid() or dt_nascimento == dt_criacao:
            return None

        idade = dt_criacao.year() - dt_nascimento.year()
        if (dt_criacao.month(), dt_criacao.day()) < (dt_nascimento.month(), dt_nascimento.day()):
            idade -= 1

        return idade


def format_and_add_to_list(list_widget: QtWidgets.QListWidget, data: dict):
    path = data.get("_path")
    item = QtWidgets.QListWidgetItem(list_widget)
    widget = ProjectItemWidget(data)

    item.setSizeHint(QtCore.QSize(widget.sizeHint().width(), 28))
    item.setData(QtCore.Qt.UserRole, path)

    list_widget.addItem(item)
    list_widget.setItemWidget(item, widget)