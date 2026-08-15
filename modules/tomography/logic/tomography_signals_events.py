from __future__ import annotations
from PySide6 import QtCore
from typing import Dict, Any


class TomographyEventTypes:
    """Constantes para os nomes dos eventos globais do EventBus suportados pelo módulo."""
    DICOM_LOADED = "DICOM_LOADED"
    DICOM_VALIDATED = "DICOM_VALIDATED"
    WINDOW_LEVEL_CHANGED = "WINDOW_LEVEL_CHANGED"


class TomographySignals(QtCore.QObject):
    """
    Barramento de sinais Qt centralizado e exclusivo para o módulo de Tomografia.
    Gerencia a comunicação reativa interna entre os componentes visuais e o controller.
    """

    # Sinais internos do Qt
    dicom_loaded = QtCore.Signal(object, str)  # (image_data, path)
    validation_status_changed = QtCore.Signal(bool, str)  # (is_valid, error_message)
    window_level_changed = QtCore.Signal(float, float)  # (window, level)

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def create_dicom_payload(volume: Any, path: str) -> Dict[str, Any]:
        """Utilitário para padronizar o payload enviado para o EventBus global."""
        return {
            "volume": volume,
            "path": path
        }