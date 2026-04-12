import json
import logging
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any


class ProjectManager:
    """
    Gerencia a persistência de dados do sistema, incluindo o ciclo de vida 
    de projetos de pacientes e arquivos de fluxos de trabalho.
    """

    def __init__(self, pasta_pacientes: Path, pasta_fluxos: Path):
        self.pasta_pacientes = Path(pasta_pacientes)
        self.pasta_fluxos = Path(pasta_fluxos)

        # Garante a existência dos diretórios base
        self.pasta_pacientes.mkdir(exist_ok=True)
        self.pasta_fluxos.mkdir(exist_ok=True)

    # --- GERENCIAMENTO DE PROJETOS ---

    def listar_projetos_recentes(self) -> List[Dict[str, Any]]:
        """
        Varre a pasta de pacientes em busca de arquivos info.json dentro 
        da subpasta 'projeto' de cada paciente.
        """
        projetos = []
        if not self.pasta_pacientes.exists():
            return projetos

        # Busca padrão: pacientes/NOME_PACIENTE/projeto/info.json
        for info_path in self.pasta_pacientes.glob("*/projeto/info.json"):
            try:
                with open(info_path, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                # Injeta o caminho da pasta raiz do paciente para referência na UI
                dados["_caminho_local"] = str(info_path.parent.parent)
                projetos.append(dados)
            except Exception as e:
                logging.error(f"Falha ao ler metadados do projeto em {info_path}: {e}")

        # Ordenação por data de criação (se disponível nos dados)
        try:
            projetos.sort(key=lambda x: x.get("data_criacao", ""), reverse=True)
        except Exception:
            pass

        return projetos

    def salvar_projeto(self, caminho_projeto: Path, dados: Dict[str, Any]):
        """
        Salva ou atualiza o arquivo info.json de um projeto específico.
        """
        try:
            raiz_projeto = Path(caminho_projeto)
            pasta_meta = raiz_projeto / "projeto"
            pasta_meta.mkdir(parents=True, exist_ok=True)

            arquivo_info = pasta_meta / "info.json"
            with open(arquivo_info, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            logging.info(f"Dados do projeto salvos em: {arquivo_info}")
        except Exception as e:
            logging.error(f"Erro crítico ao salvar projeto em {caminho_projeto}: {e}")
            raise

    def remover_projeto(self, caminho_projeto: str) -> bool:
        """
        Remove permanentemente a pasta inteira do projeto (paciente).
        """
        try:
            caminho = Path(caminho_projeto)
            if caminho.exists() and caminho.is_dir():
                shutil.rmtree(caminho)
                logging.info(f"Diretório do projeto removido: {caminho}")
                return True
            return False
        except Exception as e:
            logging.error(f"Erro ao tentar excluir projeto {caminho_projeto}: {e}")
            return False

    # --- GERENCIAMENTO DE FLUXOS ---

    def listar_fluxos_disponiveis(self, ignorar_arquivo: str = None) -> List[Dict[str, Any]]:
        """
        Lista todos os arquivos .json na pasta de fluxos.
        """
        fluxos = []
        if not self.pasta_fluxos.exists():
            return fluxos

        for path in self.pasta_fluxos.glob("*.json"):
            # Permite ignorar arquivos específicos (ex: o fluxo de cadastro padrão)
            if ignorar_arquivo and path.name == Path(ignorar_arquivo).name:
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                # Atributos auxiliares para a interface
                dados["_caminho_arquivo"] = str(path)
                fluxos.append(dados)
            except Exception as e:
                logging.error(f"Falha ao processar arquivo de fluxo {path}: {e}")

        return fluxos

    def remover_fluxo(self, caminho_fluxo: str) -> bool:
        """
        Remove um arquivo individual de fluxo (.json).
        """
        try:
            caminho = Path(caminho_fluxo)
            if caminho.exists() and caminho.is_file():
                os.remove(caminho)
                logging.info(f"Arquivo de fluxo excluído: {caminho}")
                return True
            return False
        except Exception as e:
            logging.error(f"Erro ao excluir fluxo em {caminho_fluxo}: {e}")
            return False