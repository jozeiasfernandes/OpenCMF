import pydicom
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, Callable, Optional

from application.scene.events.scene_events import SceneEvents

# Settings
from core.settings.localization.translator import tr


class DicomValidator:
    def __init__(self, event_bus: Any = None):
        self.event_bus = event_bus

    def validate_directory(self, caminho_origem: Path, callback: Optional[Callable] = None) -> Dict[str, Any]:
        if not caminho_origem.exists():
            return {"sucesso": False, "erro": tr("file_browser.create_folder_error", "Caminho não encontrado.")}

        series_map = defaultdict(list)

        extensoes_ignoradas = {".txt", ".pdf", ".docx", ".png", ".jpg", ".ini", ".json"}
        arquivos = [
            f for f in caminho_origem.rglob("*")
            if f.is_file() and not f.name.startswith('.') and f.suffix.lower() not in extensoes_ignoradas
        ]

        total_arquivos = len(arquivos)
        if total_arquivos == 0:
            return {"sucesso": False, "erro": tr("dialogs.error.message", "Nenhum arquivo compatível encontrado na pasta.")}

        for i, arquivo in enumerate(arquivos):
            if callback and i % 10 == 0:
                callback(f"Analisando: {arquivo.name}", int((i / total_arquivos) * 100))

            try:
                with open(arquivo, 'rb') as f:
                    f.seek(128)
                    if f.read(4) != b"DICM":
                        continue

                ds = pydicom.dcmread(arquivo, stop_before_pixels=True, force=True)

                modalidade = str(getattr(ds, "Modality", "")).upper()
                image_type = getattr(ds, "ImageType", [])
                if isinstance(image_type, str):
                    image_type = [image_type]
                image_type_str = " ".join([str(t) for t in image_type]).upper()

                modalidades_validas = {"CT", "PT", "MR"}

                if modalidade and modalidade not in modalidades_validas:
                    continue

                if "LOCALIZER" in image_type_str or "SCOUT" in image_type_str:
                    continue

                series_uid = getattr(ds, 'SeriesInstanceUID', 'unknown')
                rows = getattr(ds, 'Rows', 0)
                columns = getattr(ds, 'Columns', 0)
                geo_key = f"{series_uid}_{rows}x{columns}"

                series_desc = getattr(ds, 'SeriesDescription', 'Série s/ nome')
                instance_number = int(getattr(ds, "InstanceNumber", 0))

                series_map[geo_key].append({
                    "path": str(arquivo),
                    "description": series_desc,
                    "instance_number": instance_number,
                    "rows": rows,
                    "columns": columns,
                    "series_uid": series_uid
                })
            except Exception:
                continue

        if not series_map:
            error_msg = "Nenhuma série tomográfica válida encontrada."
            # Opcional: só emite se o event_bus possuir suporte ao método emit
            if self.event_bus and hasattr(self.event_bus, "emit"):
                try:
                    self.event_bus.emit("ERROR_OCCURRED", message=error_msg)
                except Exception:
                    pass
            return {"sucesso": False, "erro": error_msg}

        return {"sucesso": True, "series": dict(series_map)}