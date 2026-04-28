import shutil
from pathlib import Path
from PySide6 import QtWidgets


class FileImporter:
    @staticmethod
    def import_files_to_patient(patient_path: str) -> bool:
        if not patient_path:
            QtWidgets.QMessageBox.warning(None, "Import", "Nenhum paciente ativo encontrado.")
            return False

        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            None,
            "Selecionar Arquivos para Importar",
            "",
            "Arquivos Suportados (*.stl *.obj *.ply *.dcm);;Arquivos de Malha (*.stl *.obj *.ply);;DICOM (*.dcm)"
        )

        if not files:
            return False

        base_path = Path(patient_path)
        success_count = 0

        extension_map = {
            '.stl': 'STL',
            '.obj': 'STL',
            '.ply': 'STL',
            '.dcm': 'DICOM'
        }

        for file_path in files:
            source = Path(file_path)
            ext = source.suffix.lower()

            subfolder = extension_map.get(ext, "OUTROS")
            target_dir = base_path / subfolder

            try:
                target_dir.mkdir(parents=True, exist_ok=True)

                destination = target_dir / source.name

                if destination.exists():
                    base_name = source.stem
                    counter = 1
                    while (target_dir / f"{base_name}_{counter}{ext}").exists():
                        counter += 1
                    destination = target_dir / f"{base_name}_{counter}{ext}"

                shutil.copy2(source, destination)
                success_count += 1
            except Exception as e:
                print(f"Erro ao importar {source.name} para {subfolder}: {e}")

        return success_count > 0