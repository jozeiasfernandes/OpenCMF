import re
import requests

def search_zip_code_online(cep_texto):
    cep = re.sub(r'\D', '', cep_texto)
    if len(cep) != 8:
        return None
    try:
        r = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=5)
        if r.status_code == 200:
            dados = r.json()
            if "erro" not in dados:
                return {
                    "logradouro": dados.get("logradouro", ""),
                    "cidade": dados.get("localidade", ""),
                    "estado": dados.get("uf", ""),
                    "pais": "Brasil"
                }
    except:
        return None
    return None

def format_directory_name(nome_paciente, timestamp):
    nome_limpo = nome_paciente.replace(' ', '_').upper()
    return f"PRJ_{int(timestamp)}_{nome_limpo}"