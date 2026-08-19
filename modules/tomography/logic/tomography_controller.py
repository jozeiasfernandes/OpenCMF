from __future__ import annotations

import logging
import json
import vtk
from pathlib import Path
from typing import Optional, Any

# Patient
from core.application.patient.patient_manager import PatientManager

# Volume
from domain.volume.dicom.engines.dicom_engine import DicomEngine
from domain.volume.dicom.validators.dicom_validator import DicomValidator

logger = logging.getLogger(f"OpenCMF.Module.{__name__.split('.')[-1]}")


class TomographyController:
    """Controlador responsável por toda a lógica de negócios e manipulação de dados do módulo de Tomografia."""

    def __init__(self, module_instance: Any):
        self.module = module_instance
        self.context = getattr(module_instance, "app_context", None)
        self.event_bus = getattr(module_instance, "event_bus", None)

        self.engine = DicomEngine(event_bus=self.event_bus)
        self.pasta_paciente: Optional[str] = None
        self.caminho_dicom: Optional[str] = None

    # =========================================================================
    # CONFIGURATION & INITIALIZATION
    # =========================================================================
    def load_project_configs(self, path_paciente: str) -> None:
        """Agora delega a inicialização e obtenção do path DICOM para o PatientManager injetado."""
        self.pasta_paciente = path_paciente
        if not self.pasta_paciente:
            return

        try:
            patient_manager = getattr(self, 'patient_manager', None)
            if not patient_manager and hasattr(self, 'context') and self.context:
                patient_manager = getattr(self.context, 'patient_manager', None)

            if not patient_manager:
                logger.error("[TomographyController] PatientManager não foi injetado ou encontrado no contexto.")
                return

            # Garante que o patient_manager está com este paciente ativo
            if patient_manager.current_path != str(Path(path_paciente).resolve()):
                patient_manager.set_active_patient(path_paciente)

            # Recupera o path DICOM diretamente dos dados já carregados pelo gerenciador
            project_data = patient_manager.data
            self.caminho_dicom = project_data.get("caminhos", {}).get("dicom")

            if self.caminho_dicom:
                logger.info(f"[TomographyController] Caminho DICOM obtido via PatientManager: {self.caminho_dicom}")
            else:
                logger.warning(f"[TomographyController] Caminho DICOM não encontrado nos dados do projeto gerenciados.")

        except Exception as e:
            logger.error(f"[TomographyController] Erro ao interagir com o PatientManager: {e}")

    # =========================================================================
    # DICOM PROCESSING & VALIDATION
    # =========================================================================
    def validate_dicom(self) -> None:
        if not self.caminho_dicom or not self.pasta_paciente:
            logger.warning(
                "[TomographyController] validate_dicom abortado: caminho_dicom ou pasta_paciente ausentes.")
            return

        try:
            validador = DicomValidator(event_bus=self.event_bus)

            # Garante que se o path salvo no json for relativo, ele se baseia na pasta do paciente
            caminho_path = Path(self.caminho_dicom)
            if not caminho_path.is_absolute():
                caminho_path = Path(self.pasta_paciente) / caminho_path

            logger.info(f"[TomographyController] Validando diretório DICOM: {caminho_path}")
            resultado = validador.validate_directory(caminho_path)

            components = getattr(self.module, "components", None)
            signals = getattr(self.module, "signals", None)

            if resultado.get("sucesso", False):
                logger.info("[TomographyController] Diretório DICOM validado com sucesso!")
                toolbar = components.toolbar_handler if components else None
                if toolbar and hasattr(toolbar, 'set_validation_state'):
                    toolbar.set_validation_state(True)

                sucesso, volume_model = self.engine.load_folder(caminho_path)
                viewer = components.viewer if components else None
                if sucesso and volume_model and viewer:
                    logger.info(
                        "[TomographyController] Volume carregado pelo engine e injetado diretamente no viewer.")
                    viewer.set_volume(volume_model.image_data)
                    self.generate_vti(volume_model.image_data)
                    if signals:
                        signals.dicom_loaded.emit(volume_model.image_data, str(caminho_path))
            else:
                msg = resultado.get('erro', 'Desconhecido')
                logger.warning(f"[TomographyController] Diretório DICOM inválido: {msg}")
                if signals:
                    signals.validation_status_changed.emit(False, msg)
        except Exception as e:
            logger.error(f"[TomographyController] Erro crítico durante a validação DICOM: {e}")

    def handle_dicom_loaded_event(self, **kwargs) -> None:
        """Callback acionado globalmente quando uma nova tomografia é importada com sucesso."""
        logger.info(f"[TomographyController] Evento 'DICOM_LOADED' capturado. Chaves: {list(kwargs.keys())}")

        volume_model = kwargs.get("volume")
        path_str = kwargs.get("path")

        if path_str:
            self.caminho_dicom = path_str

        components = getattr(self.module, "components", None)
        viewer = components.get_central_area() if components else None

        if volume_model and viewer:
            image_data = getattr(volume_model, "image_data", volume_model)
            logger.info("[TomographyController] Repassando dados de imagem para o VolumeViewerWidget.")
            viewer.set_volume(image_data)
            self.generate_vti(image_data)
        else:
            logger.warning(
                "[TomographyController] Evento 'DICOM_LOADED' recebido, mas 'volume' ou 'viewer' ausentes.")

        toolbar = components.toolbar_handler if components else None
        if toolbar and hasattr(toolbar, 'set_validation_state'):
            toolbar.set_validation_state(True)

    def generate_vti(self, vtk_image_data: Any) -> None:
        if not vtk_image_data or not self.pasta_paciente:
            return
        try:
            pasta_projeto = Path(self.pasta_paciente) / "projeto"
            pasta_projeto.mkdir(parents=True, exist_ok=True)

            path_vti = pasta_projeto / "volume.vti"
            writer = vtk.vtkXMLImageDataWriter()
            writer.SetFileName(str(path_vti))
            writer.SetInputData(vtk_image_data)
            writer.Write()
            logger.info(f"[TomographyController] Volume VTI gerado com sucesso em: {path_vti}")
        except Exception as e:
            logger.error(f"[TomographyController] Erro ao gerar arquivo VTI: {e}")

    # =========================================================================
    # VIEW & STATE UPDATES
    # =========================================================================
    def update_window_level(self, window: float, level: float) -> None:
        components = getattr(self.module, "components", None)
        viewer = components.viewer if components else None
        if viewer:
            viewer.update_window_level(window, level)

    def complete_stage(self) -> None:
        pass

    # =========================================================================
    # CLEANUP
    # =========================================================================
    def cleanup(self) -> None:
        self.engine = None
        logger.info("[TomographyController] Limpeza do controlador executada com sucesso.")