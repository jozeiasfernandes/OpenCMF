from __future__ import annotations

from PySide6 import QtWidgets, QtGui, QtCore
from domain.volume.visualization.lut.lut_presets import LUTPresets


class LUTDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        name = index.data()
        stops = LUTPresets.PRESETS.get(name, [])
        rect = option.rect

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Desenha fundo de seleção se estiver selecionado ou sob o mouse
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            painter.fillRect(rect, option.palette.alternateBase())

        # Cria o gradiente linear horizontal para o fundo do item
        grad_rect = rect.adjusted(3, 2, -3, -2)
        if stops:
            gradient = QtGui.QLinearGradient(grad_rect.left(), 0, grad_rect.right(), 0)
            for pos, hex_val in stops:
                gradient.setColorAt(pos, QtGui.QColor(hex_val))

            painter.setBrush(gradient)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRoundedRect(grad_rect, 4, 4)

        # Desenha o texto com sombra/contorno para garantir legibilidade sobre qualquer gradiente
        text_rect = rect.adjusted(1, 1, 1, 1)
        painter.setFont(option.font)

        # Sombra sutil do texto
        painter.setPen(QtGui.QColor(0, 0, 0, 200))
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, name)

        # Texto principal em branco ou cor contrastante
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(rect, QtCore.Qt.AlignCenter, name)

        painter.restore()

    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtCore.QSize:
        return QtCore.QSize(120, 28)