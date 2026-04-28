import shutil
from pathlib import Path
from PySide6 import QtWidgets


class FileImporter:
    @staticmethod
    def import_stl_to_patient(patient_path: str) -> bool:
        if not patient_path:
            QtWidgets.QMessageBox.warning(None, "Import", "Nenhum paciente ativo encontrado.")
            return False

        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            None,
            "Selecionar Arquivos STL",
            "",
            "Mesh Files (*.stl)"
        )

        if not files:
            return False

        # Define a estrutura padrão: pasta_do_paciente/STL/
        target_dir = Path(patient_path) / "STL"
        target_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        for file_path in files:
            source = Path(file_path)
            destination = target_dir / source.name

            try:
                # copy2 preserva metadados do arquivo
                shutil.copy2(source, destination)
                success_count += 1
            except Exception as e:
                print(f"Erro ao importar {source.name}: {e}")

        return success_count > 0