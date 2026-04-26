import zipfile
import shutil
import pydicom
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, Callable, Optional


class DicomValidator:
    def __init__(self, pasta_projeto_paciente: str):
        self.pasta_projeto = Path(pasta_projeto_paciente)
        self.temp_dir = self.pasta_projeto / "projeto" / "temp_dicom"

    def analisar_caminho(self, caminho_origem: str, callback: Optional[Callable[[str, int], None]] = None) -> Dict[
        str, Any]:
        path_origem = Path(caminho_origem)

        if not path_origem.exists():
            return {"sucesso": False, "erro": "Caminho não encontrado."}

        if path_origem.is_file() and path_origem.suffix.lower() == ".zip":
            if callback: callback("Extraindo arquivos ZIP...", 0)
            caminho_trabalho = self._extrair_zip(path_origem)
            if not caminho_trabalho:
                return {"sucesso": False, "erro": "Falha ao extrair arquivo ZIP."}
        else:
            caminho_trabalho = path_origem

        series_map = defaultdict(list)
        arquivos = [f for f in caminho_trabalho.rglob("*") if f.is_file()]
        total_arquivos = len(arquivos)

        if total_arquivos == 0:
            return {"sucesso": False, "erro": "A pasta selecionada está vazia."}

        for i, arquivo in enumerate(arquivos):
            if callback and i % 5 == 0:
                percentual = int((i / total_arquivos) * 100)
                callback(f"Analisando: {arquivo.name}", percentual)

            try:
                with open(arquivo, 'rb') as f:
                    f.seek(128)
                    if f.read(4) != b"DICM":
                        continue

                ds = pydicom.dcmread(arquivo, stop_before_pixels=True)

                if ds.Modality != "CT":
                    continue

                # Captura geometria para evitar erro de Shape
                rows = getattr(ds, "Rows", 0)
                cols = getattr(ds, "Columns", 0)
                s_id = ds.SeriesInstanceUID

                # Chave única por Série + Resolução
                geo_key = f"{s_id}_{rows}x{cols}"

                series_map[geo_key].append({
                    "path": str(arquivo),
                    "desc": f"{ds.get('SeriesDescription', 'Série')} ({rows}x{cols})",
                    "instancia": int(ds.get("InstanceNumber", 0)),
                    "rows": rows,
                    "cols": cols
                })
            except Exception:
                continue

        if not series_map:
            return {"sucesso": False, "erro": "Nenhuma série de Tomografia (CT) válida encontrada."}

        return {"sucesso": True, "series": series_map}

    def _extrair_zip(self, caminho_zip: Path) -> Optional[Path]:
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            return self.temp_dir
        except Exception:
            return None

    def limpar_temporarios(self) -> None:
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)