from __future__ import annotations
from typing import Optional, Any, Dict, Tuple
from pathlib import Path
from PySide6 import QtWidgets

from core.application.patient.patient_manager import PatientManager

# Importações dos componentes do domínio
from domain.volume.dicom.engines.dicom_engine import DicomEngine
from domain.volume.windows.dicom_import_dialog import DicomImportWindow
from domain.volume.windows.volume_orientation_dialog import VolumeOrientationWindow


class DicomImportPipeline:
    """Pipeline responsável por gerenciar o fluxo de estados para importação de DICOM."""

    def __init__(
        self,
        engine: Optional[DicomEngine] = None,
        event_bus: Optional[Any] = None,
        parent: Optional[QtWidgets.QWidget] = None,
        scene: Optional[Any] = None
    ):
        self.engine = engine or DicomEngine()
        self.event_bus = event_bus
        self.parent = parent
        self.scene = scene

        # Estado interno do Pipeline
        self.caminho_dicom: Optional[Path] = None
        self.series_disponiveis: list[Dict[str, Any]] = []
        self.serie_selecionada: Optional[Dict[str, Any]] = None
        self.fatores_amostragem: Tuple[float, float, float] = (1.0, 1.0, 1.0)
        self.parametros_orientacao: Dict[str, Any] = {}

    def start(self, caminho: str | Path):
        """Ponto de entrada do pipeline de importação."""
        self.caminho_dicom = Path(caminho)

        # 1. Obter lista de séries via Engine
        try:
            self.series_disponiveis = self.engine.get_series_list(self.caminho_dicom)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.parent,
                "Erro de Leitura",
                f"Ocorreu um erro ao varrer o diretório DICOM:\n{str(e)}"
            )
            return

        if not self.series_disponiveis:
            QtWidgets.QMessageBox.warning(
                self.parent,
                "Aviso",
                "Nenhuma série DICOM válida foi encontrada no diretório selecionado."
            )
            return

        # 2. Sempre abre a janela de seleção
        self.open_series_selection()

    def open_series_selection(self):
        """Etapa de escolha da série e definição de fatores de amostragem."""
        dialog = DicomImportWindow(series_list=self.series_disponiveis, parent=self.parent)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.serie_selecionada = dialog.get_selected_series()
            self.fatores_amostragem = dialog.get_sampling_factors()
            self.guidance_step()

    def guidance_step(self):
        """Etapa para verificação de orientação, rotação e ROI."""
        dialog = VolumeOrientationWindow(volume_data=self.serie_selecionada, parent=self.parent)

        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.parametros_orientacao = dialog.get_orientation_parameters()
            self.load_final_volume()

    def load_final_volume(self):
        """Passo final: Processa o volume no engine e injeta no sistema via EventBus."""
        if not self.serie_selecionada:
            return

        try:
            target_path = self.serie_selecionada.get("path", self.caminho_dicom)
            sucesso, volume_model = self.engine.load_folder(Path(target_path))

            if sucesso and volume_model:
                # Acesso seguro ao patient_manager via contexto da aplicação (sem Singleton)
                try:
                    patient_manager = getattr(self, 'patient_manager', None)
                    if not patient_manager and hasattr(self, 'context') and self.context:
                        patient_manager = getattr(self.context, 'patient_manager', None)

                    if patient_manager and hasattr(patient_manager, 'current_path'):
                        current_patient = patient_manager.current_path
                        if current_patient and hasattr(volume_model, 'patient_dir'):
                            volume_model.patient_dir = current_patient
                except Exception:
                    pass  # Ignora se o PatientManager não estiver acessível neste escopo

                # Emite o evento global de forma segura se o event_bus estiver configurado
                event_bus = getattr(self, 'event_bus', None)
                if not event_bus and hasattr(self, 'context') and self.context:
                    event_bus = getattr(self.context, 'event_bus', None)

                if event_bus and hasattr(event_bus, 'emit'):
                    event_bus.emit("DICOM_LOADED", volume=volume_model.image_data)
                else:
                    print("Volume DICOM carregado com sucesso (EventBus não configurado).")
            else:
                QtWidgets.QMessageBox.critical(
                    self.parent,
                    "Erro de Processamento",
                    "O engine não conseguiu gerar o modelo volumétrico a partir dos arquivos."
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self.parent,
                "Erro Crítico",
                f"Falha inesperada ao carregar o volume final:\n{str(e)}"
            )