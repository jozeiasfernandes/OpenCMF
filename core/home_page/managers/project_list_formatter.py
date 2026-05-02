from PySide6 import QtWidgets, QtCore


class ProjectItemWidget(QtWidgets.QWidget):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        info_layout = QtWidgets.QVBoxLayout()

        paciente = self.data.get("paciente", {})
        nome = paciente.get("nome", "Sem Nome")
        sexo = paciente.get("sexo", "N/A")

        lbl_nome = QtWidgets.QLabel(f"<b>{nome}</b>")
        lbl_info = QtWidgets.QLabel(f" Sexo: {sexo}")
        lbl_info.setStyleSheet("color: #888; font-size: 11px;")

        info_layout.addWidget(lbl_nome)
        info_layout.addWidget(lbl_info)

        timestamp = self.data.get("created_at", 0)
        data_dt = QtCore.QDateTime.fromSecsSinceEpoch(int(timestamp))
        lbl_data = QtWidgets.QLabel(data_dt.toString("dd/MM/yyyy HH:mm"))
        lbl_data.setStyleSheet("color: #666; font-size: 10px;")

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(lbl_data)


def format_and_add_to_list(list_widget: QtWidgets.QListWidget, data: dict):
    path = data.get("_path")
    item = QtWidgets.QListWidgetItem(list_widget)
    widget = ProjectItemWidget(data)

    item.setSizeHint(widget.sizeHint())
    item.setData(QtCore.Qt.UserRole, path)

    list_widget.addItem(item)
    list_widget.setItemWidget(item, widget)