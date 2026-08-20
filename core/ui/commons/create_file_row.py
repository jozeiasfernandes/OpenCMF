from PySide6 import QtWidgets, QtCore

def create_file_row(edit_widget, callback_function, folder=True):
    widget_row = QtWidgets.QWidget()
    layout_row = QtWidgets.QHBoxLayout(widget_row)
    layout_row.setContentsMargins(0, 0, 0, 0)

    layout_row.addWidget(edit_widget)

    search_button = QtWidgets.QToolButton()
    search_button.setText("...")
    search_button.setCursor(QtCore.Qt.PointingHandCursor)

    search_button.clicked.connect(lambda: callback_function(edit_widget, folder))

    layout_row.addWidget(search_button)

    return widget_row