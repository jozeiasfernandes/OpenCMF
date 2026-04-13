import json
import logging
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class ProjectManager:
    """
    Gerencia a persistência de dados de projetos de pacientes e fluxos de trabalho.
    """

    def __init__(self, pasta_pacientes: Path, pasta_fluxos: Path):
        self.pasta_pacientes = Path(pasta_pacientes)
        self.pasta_fluxos = Path(pasta_fluxos)

        self._garantir_diretorios()

    def _garantir_diretorios(self) -> None:
        self.pasta_pacientes.mkdir(parents=True, exist_ok=True)
        self.pasta_fluxos.mkdir(parents=True, exist_ok=True)

    # --- AUXILIARES ---

    def _carregar_json(self, caminho: Path) -> Optional[Dict[str, Any]]:
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Erro ao carregar JSON em {caminho}: {e}")
            return None

    # --- GERENCIAMENTO DE PROJETOS ---

    def listar_projetos_recentes(self) -> List[Dict[str, Any]]:
        projetos = []
        arquivos_info = self.pasta_pacientes.glob("*/projeto/info.json")

        for caminho in arquivos_info:
            dados = self._carregar_json(caminho)
            if dados:
                dados["_caminho_local"] = str(caminho.parents[1])

                # FALLBACK: Se não houver data_criacao no JSON, usa a data do sistema
                if "data_criacao" not in dados:
                    dados["data_criacao"] = caminho.stat().st_mtime

                projetos.append(dados)

        # Ordenação decrescente (mais recentes primeiro)
        return self._ordenar_projetos(projetos)

    def _ordenar_projetos(self, projetos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # reverse=True coloca o maior valor (data mais recente) no topo
        return sorted(
            projetos,
            key=lambda x: x.get("data_criacao", ""),
            reverse=True
        )

    def _ordenar_projetos(self, projetos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ordena os projetos garantindo que todos os tipos de data sejam comparáveis."""

        def chave_ordenacao(proj):
            data = proj.get("data_criacao", "")
            # Se a data for um número (float/int), converte para string
            if isinstance(data, (int, float)):
                return str(data)
            # Se for None ou algo vazio, retorna uma string vazia para ir pro final da lista
            if data is None:
                return ""
            return str(data)

        return sorted(
            projetos,
            key=chave_ordenacao,
            reverse=True
        )

    def salvar_projeto(self, caminho_raiz: Path, dados: Dict[str, Any]) -> None:
        try:
            pasta_meta = Path(caminho_raiz) / "projeto"
            pasta_meta.mkdir(parents=True, exist_ok=True)

            arquivo_info = pasta_meta / "info.json"

            with open(arquivo_info, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            logging.info(f"Projeto salvo: {arquivo_info}")
        except Exception as e:
            logging.error(f"Erro ao salvar projeto em {caminho_raiz}: {e}")
            raise

    def remover_projeto(self, caminho_projeto: str) -> bool:
        try:
            caminho = Path(caminho_projeto)
            if caminho.is_dir():
                shutil.rmtree(caminho)
                logging.info(f"Projeto removido: {caminho}")
                return True
            return False
        except Exception as e:
            logging.error(f"Falha ao remover projeto {caminho_projeto}: {e}")
            return False

    # --- GERENCIAMENTO DE FLUXOS ---

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
                logging.info(f"Fluxo removido: {caminho}")
                return True
            return False
        except Exception as e:
            logging.error(f"Falha ao remover fluxo {caminho_fluxo}: {e}")
            return False