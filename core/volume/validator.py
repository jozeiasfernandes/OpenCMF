import pydicom
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, Callable, Optional
from core.scene.events.scene_events import SceneEvents

class DicomValidator:
    def __init__(self, event_bus: Any = None):
        self.event_bus = event_bus

    def validar_diretorio(self, caminho_origem: Path, callback: Optional[Callable] = None) -> Dict[str, Any]:
        if not caminho_origem.exists():
            return {"sucesso": False, "erro": "Caminho não encontrado."}

        series_map = defaultdict(list)
        arquivos = [f for f in caminho_origem.rglob("*") if f.is_file() and not f.name.startswith('.')]

        if not arquivos:
            return {"sucesso": False, "erro": "Pasta vazia."}

        for i, arquivo in enumerate(arquivos):
            if callback and i % 10 == 0:
                callback(f"Analisando: {arquivo.name}", int((i / len(arquivos)) * 100))
            try:
                with open(arquivo, 'rb') as f:
                    if f.read(132)[128:132] != b"DICM":
                        continue
                ds = pydicom.dcmread(arquivo, stop_before_pixels=True)

                if ds.Modality != "CT" or "LOCALIZER" in getattr(ds, "ImageType", []):
                    continue

                geo_key = f"{ds.SeriesInstanceUID}_{ds.Rows}x{ds.Columns}"
                series_map[geo_key].append({
                    "path": str(arquivo),
                    "desc": f"{ds.get('SeriesDescription', 'Série s/ nome')} ({ds.Rows}x{ds.Columns})",
                    "instancia": int(ds.get("InstanceNumber", 0))
                })
            except Exception:
                continue

        if not series_map:
            if self.event_bus:
                self.event_bus.emit(SceneEvents.ERROR_OCCURRED, message="Nenhuma série CT válida encontrada.")
            return {"sucesso": False, "erro": "Nenhuma série CT válida encontrada."}

        return {"sucesso": True, "series": dict(series_map)}