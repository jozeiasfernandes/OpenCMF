from pathlib import Path
from typing import Any, Dict


def formatar_info_exame(ds: Any) -> Dict[str, str]:
    nome_paciente = str(ds.get("PatientName", "Anônimo"))
    data_estudo = ds.get("StudyDate", "N/A")
    modalidade = ds.get("Modality", "N/A")
    espessura = ds.get("SliceThickness", 0)

    return {
        "paciente": nome_paciente,
        "data": data_estudo,
        "modalidade": modalidade,
        "espessura": f"{float(espessura):.2f} mm",
        "dimensoes": f"{ds.Rows}x{ds.Columns}"
    }


def calcular_espaco_disco(caminho_pasta: str) -> str:
    diretorio = Path(caminho_pasta)
    bytes_totais = sum(f.stat().st_size for f in diretorio.rglob('*') if f.is_file())
    megabytes = bytes_totais / (1024 * 1024)

    return f"{megabytes:.2f} MB"


def limpar_nomes_arquivos(pasta: str) -> None:
    pass