import pytest
from pathlib import Path
from gui.logic.project_manager import ProjectManager


def test_patient_folder_creation(tmp_path):
    """
    tmp_path é uma ferramenta do pytest que cria uma
    pasta temporária que se auto-destrói após o teste.
    """
    manager = ProjectManager(patients_dir=tmp_path, flows_dir=tmp_path)

    # Simula a criação de um paciente
    new_patient = tmp_path / "Patient_001"
    new_patient.mkdir()

    assert new_patient.exists()
    assert len(manager.listar_projetos_recentes()) == 1