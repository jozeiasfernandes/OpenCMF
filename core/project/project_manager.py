import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional


class ProjectManager:
    SUBPASTAS_PADRAO = ["projeto", "SUPERFICIES", "FOTOGRAFIAS", "VOLUME", "OUTROS"]

    def __init__(self, pasta_pacientes: Path, pasta_fluxos: Path):
        self.pasta_pacientes = Path(pasta_pacientes)
        self.pasta_fluxos = Path(pasta_fluxos)
        self._garantir_diretorios_base()

    def _garantir_diretorios_base(self) -> None:
        self.pasta_pacientes.mkdir(parents=True, exist_ok=True)
        self.pasta_fluxos.mkdir(parents=True, exist_ok=True)

    def inicializar_estrutura_paciente(self, caminho_paciente: Path) -> None:
        for subpasta in self.SUBPASTAS_PADRAO:
            (caminho_paciente / subpasta).mkdir(parents=True, exist_ok=True)

    def carregar_projeto(self, caminho_raiz: Path) -> Optional[Dict[str, Any]]:
        arquivo_info = Path(caminho_raiz) / "projeto" / "info.json"
        return self._carregar_json(arquivo_info)

    def salvar_projeto(self, caminho_raiz: Path, dados: Dict[str, Any]) -> None:
        try:
            pasta_meta = Path(caminho_raiz) / "projeto"
            pasta_meta.mkdir(parents=True, exist_ok=True)
            arquivo_info = pasta_meta / "info.json"
            with open(arquivo_info, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Erro ao salvar projeto em {caminho_raiz}: {e}")

    def copiar_e_registrar_arquivo(self, caminho_raiz: Path, arquivo_origem: Path, categoria: str, subtipo: str) -> \
    Dict[str, Any]:
        pasta_destino = Path(caminho_raiz) / categoria.upper()
        pasta_destino.mkdir(parents=True, exist_ok=True)

        nome_arquivo = arquivo_origem.name
        destino_final = pasta_destino / nome_arquivo

        if destino_final.exists():
            stem = arquivo_origem.stem
            ext = arquivo_origem.suffix
            contador = 1
            while (pasta_destino / f"{stem}_{contador}{ext}").exists():
                contador += 1
            nome_arquivo = f"{stem}_{contador}{ext}"
            destino_final = pasta_destino / nome_arquivo

        shutil.copy2(arquivo_origem, destino_final)

        return {
            "nome_exibicao": arquivo_origem.stem,
            "caminho_relativo": f"{categoria.upper()}/{nome_arquivo}",
            "categoria": categoria,
            "subtipo": subtipo
        }

    def listar_projetos_recentes(self) -> List[Dict[str, Any]]:
        projetos = []
        for caminho in self.pasta_pacientes.glob("*/projeto/info.json"):
            dados = self._carregar_json(caminho)
            if dados:
                dados["_caminho_local"] = str(caminho.parents[1])
                if "data_criacao" not in dados:
                    dados["data_criacao"] = caminho.stat().st_mtime
                projetos.append(dados)
        return self._ordenar_projetos(projetos)

    def _ordenar_projetos(self, projetos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def chave_ordenacao(proj):
            data = proj.get("data_criacao", "")
            return str(data) if data is not None else ""

        return sorted(projetos, key=chave_ordenacao, reverse=True)

    def remover_projeto(self, caminho_projeto: str) -> bool:
        try:
            caminho = Path(caminho_projeto)
            if caminho.is_dir():
                shutil.rmtree(caminho)
                return True
            return False
        except Exception as e:
            logging.error(f"Falha ao remover projeto {caminho_projeto}: {e}")
            return False

    def listar_fluxos_disponiveis(self, ignorar_nome: Optional[str] = None) -> List[Dict[str, Any]]:
        fluxos = []
        for arquivo in self.pasta_fluxos.glob("*.json"):
            if ignorar_nome and arquivo.name == Path(ignorar_nome).name:
                continue
            dados = self._carregar_json(arquivo)
            if dados:
                dados["_caminho_arquivo"] = str(arquivo)
                fluxos.append(dados)
        return fluxos

    def remover_fluxo(self, caminho_fluxo: str) -> bool:
        try:
            caminho = Path(caminho_fluxo)
            if caminho.is_file():
                caminho.unlink()
                return True
            return False
        except Exception as e:
            logging.error(f"Falha ao remover fluxo {caminho_fluxo}: {e}")
            return False

    def _carregar_json(self, caminho: Path) -> Optional[Dict[str, Any]]:
        try:
            if not caminho.exists():
                return None
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Erro ao carregar JSON em {caminho}: {e}")
            return None