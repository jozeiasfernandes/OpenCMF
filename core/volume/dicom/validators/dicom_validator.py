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

        # Filtra apenas arquivos que parecem ser DICOM ou estão em estruturas comuns,
        # ignorando arquivos ocultos e extensões óbvias de sistema/texto
        extensoes_ignoradas = {".txt", ".pdf", ".docx", ".png", ".jpg", ".ini", ".json"}
        arquivos = [
            f for f in caminho_origem.rglob("*")
            if f.is_file() and not f.name.startswith('.') and f.suffix.lower() not in extensoes_ignoradas
        ]

        total_arquivos = len(arquivos)
        if total_arquivos == 0:
            return {"sucesso": False, "erro": "Nenhum arquivo compatível encontrado na pasta."}

        for i, arquivo in enumerate(arquivos):
            if callback and i % 10 == 0:
                callback(f"Analisando: {arquivo.name}", int((i / total_arquivos) * 100))

            try:
                with open(arquivo, 'rb') as f:
                    # Verifica o preâmbulo DICOM padrão (128 bytes ignorados + 4 bytes "DICM")
                    f.seek(128)
                    if f.read(4) != b"DICM":
                        continue

                # Lê apenas os metadados sem carregar a matriz de pixels para poupar memória
                ds = pydicom.dcmread(arquivo, stop_before_pixels=True, force=True)

                # Flexibilizado para aceitar CT convencional, exames de tomografia odontológica/CBCT
                # e outras variações comuns de tomografia, evitando rejeitar exames legítimos de CTBMF.
                modalidade = str(getattr(ds, "Modality", "")).upper()
                image_type = getattr(ds, "ImageType", [])
                if isinstance(image_type, str):
                    image_type = [image_type]
                image_type_str = " ".join([str(t) for t in image_type]).upper()

                # Modalidades aceitas para reconstrução volumétrica (CT e PT/CBCT comuns na área)
                modalidades_validas = {"CT", "PT", "MR"}

                # Se a modalidade estiver vazia, permitimos passar para conferir se tem dados espaciais,
                # mas se houver uma modalidade explícita inválida, filtramos.
                if modalidade and modalidade not in modalidades_validas:
                    continue

                if "LOCALIZER" in image_type_str or "SCOUT" in image_type_str:
                    continue

                geo_key = f"{getattr(ds, 'SeriesInstanceUID', 'unknown')}_{getattr(ds, 'Rows', 0)}x{getattr(ds, 'Columns', 0)}"

                series_map[geo_key].append({
                    "path": str(arquivo),
                    "desc": f"{ds.get('SeriesDescription', 'Série s/ nome')} ({ds.Rows}x{ds.Columns})",
                    "instancia": int(ds.get("InstanceNumber", 0))
                })
            except Exception:
                # Ignora arquivos corrompidos ou que falharam na leitura do pydicom
                continue

        if not series_map:
            if self.event_bus:
                self.event_bus.emit(SceneEvents.ERROR_OCCURRED, message="Nenhuma série tomográfica válida encontrada.")
            return {"sucesso": False, "erro": "Nenhuma série tomográfica válida encontrada."}

        return {"sucesso": True, "series": dict(series_map)}