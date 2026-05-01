import re
import requests


def limpar_cep(cep: str) -> str:
    return re.sub(r"\D", "", cep or "")


def cep_valido(cep: str) -> bool:
    cep_limpo = limpar_cep(cep)
    return len(cep_limpo) == 8


def consultar_cep(cep: str) -> dict | None:
    cep_limpo = limpar_cep(cep)

    if len(cep_limpo) != 8:
        return None

    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)

        if r.status_code != 200:
            return None

        data = r.json()

        if "erro" in data:
            return None

        return {
            "logradouro": data.get("logradouro", ""),
            "cidade": data.get("localidade", ""),
            "estado": data.get("uf", ""),
            "pais": "Brasil"
        }

    except Exception:
        return None