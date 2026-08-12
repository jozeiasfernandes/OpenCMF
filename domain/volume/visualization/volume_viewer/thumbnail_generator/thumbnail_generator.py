from __future__ import annotations

import vtk
from PySide6 import QtGui, QtCore


class DicomThumbnailGenerator:
    """Gerador utilitário de miniaturas (thumbnails) para séries DICOM usando VTK e PySide6."""

    @staticmethod
    def generate_thumbnail(vtk_image: vtk.vtkImageData, target_size: int = 160) -> QtGui.QPixmap:
        """Extrai a fatia axial central de um vtkImageData e a converte em QPixmap otimizado para pré-via."""
        if not vtk_image:
            return QtGui.QPixmap()

        ext = vtk_image.GetExtent()
        dims = vtk_image.GetDimensions()

        if dims[0] <= 0 or dims[1] <= 0 or dims[2] <= 0:
            return QtGui.QPixmap()

        # Pega o corte axial do meio (eixo Z)
        mid_z = ext[4] + (dims[2] // 2)

        reslice = vtk.vtkImageReslice()
        reslice.SetInputData(vtk_image)
        reslice.SetOutputDimensionality(2)
        reslice.SetResliceAxesDirectionCosines(1, 0, 0, 0, 1, 0, 0, 0, 1)

        center = vtk_image.GetCenter()
        origin = vtk_image.GetOrigin()
        spacing = vtk_image.GetSpacing()
        z_pos = origin[2] + mid_z * spacing[2]
        reslice.SetResliceAxesOrigin(center[0], center[1], z_pos)
        reslice.Update()

        slice_data = reslice.GetOutput()

        # Converte para UNSIGNED_CHAR (8-bit) para exibição correta no QImage
        cast_filter = vtk.vtkImageCast()
        cast_filter.SetInputData(slice_data)
        cast_filter.SetOutputScalarTypeToUnsignedChar()

        # Opcional: aplica um mapeamento de janela/nível básico se necessário
        window_level = vtk.vtkImageMapToWindowLevelColors()
        window_level.SetInputConnection(cast_filter.GetOutputPort())

        # Tenta estimar uma faixa inicial de Window/Level baseada nos dados escalares
        scalar_range = slice_data.GetScalarRange()
        window = max(1.0, scalar_range[1] - scalar_range[0])
        level = 0.5 * (scalar_range[0] + scalar_range[1])
        window_level.SetWindow(window)
        window_level.SetLevel(level)
        window_level.Update()

        colored_slice = window_level.GetOutput()
        out_dims = colored_slice.GetDimensions()
        width, height = out_dims[0], out_dims[1]

        if width <= 0 or height <= 0:
            return QtGui.QPixmap()

        # Extrai os ponteiros de pixels do VTK
        pointer = colored_slice.GetPointData().GetScalars()
        if not pointer:
            return QtGui.QPixmap()

        # Converte os dados do VTK para bytes e cria um QImage
        # Como o WindowLevelColors gera RGBA ou Luminance, tratamos de forma segura
        import numpy as np
        array = vtk.util.numpy_support.vtk_to_numpy(pointer)

        # Garante o formato correto para o QImage (geralmente RGBA ou Escala de Cinza)
        if colored_slice.GetNumberOfScalarComponents() == 4:
            q_format = QtGui.QImage.Format_RGBA8888
        elif colored_slice.GetNumberOfScalarComponents() == 3:
            q_format = QtGui.QImage.Format_RGB888
        else:
            q_format = QtGui.QImage.Format_Grayscale8

        # Remodela ou copia para o buffer do QImage
        image_bytes = array.tobytes()
        q_image = QtGui.QImage(image_bytes, width, height, width * colored_slice.GetNumberOfScalarComponents(),
                               q_format)

        # O VTK armazena a imagem invertida verticalmente em relação ao padrão do Qt
        q_image = q_image.mirrored(False, True)

        # Converte em QPixmap e redimensiona com alta qualidade mantendo proporção
        pixmap = QtGui.QPixmap.fromImage(q_image)
        return pixmap.scaled(target_size, target_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)