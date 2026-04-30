import shutil
from pathlib import Path
from PySide6 import QtWidgets

class FileImporter:
    @staticmethod
    def import_files_to_patient(patient_path: str) -> list[Path]:
        if not patient_path:
            QtWidgets.QMessageBox.warning(None, "Import", "Nenhum paciente ativo encontrado.")
            return []

        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            None,
            "Selecionar Arquivos para Importar",
            "",
            "Malhas (*.stl *.obj *.ply);;DICOM (*.dcm);;Todos (*.*)"
        )

        if not files:
            return []

        base_path = Path(patient_path)
        imported_paths = []

        extension_map = {
            '.stl': 'SUPERFICIES',
            '.obj': 'SUPERFICIES',
            '.ply': 'SUPERFICIES',
            '.dcm': 'VOLUME'
        }

        for file_path in files:
            source = Path(file_path)
            ext = source.suffix.lower()
            subfolder = extension_map.get(ext, "OUTROS")
            target_dir = base_path / subfolder

            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                destination = target_dir / source.name

                # Evitar sobrescrever arquivos com o mesmo nome
                if destination.exists():
                    counter = 1
                    while (target_dir / f"{source.stem}_{counter}{ext}").exists():
                        counter += 1
                    destination = target_dir / f"{source.stem}_{counter}{ext}"

                shutil.copy2(source, destination)
                imported_paths.append(destination)
            except Exception as e:
                print(f"Erro ao importar {source.name}: {e}")

        return imported_paths