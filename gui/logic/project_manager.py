import json
import logging
from pathlib import Path
from typing import List, Dict, Any


class ProjectManager:
    def __init__(self, pasta_pacientes: Path, pasta_fluxos: Path):
        self.pasta_pacientes = Path(pasta_pacientes)
        self.pasta_fluxos = Path(pasta_fluxos)
        self.pasta_pacientes.mkdir(exist_ok=True)

    def listar_projetos_recentes(self) -> List[Dict[str, Any]]:
        """
        Busca info.json especificamente na estrutura:
        pacientes/PASTA_DO_PACIENTE/projeto/info.json
        """
        projetos = []
        if not self.pasta_pacientes.exists():
            return projetos

        # Usamos um padrão mais específico para evitar ler arquivos JSON perdidos
        # Procure por qualquer pasta, que tenha uma subpasta 'projeto', que tenha um 'info.json'
        for info_path in self.pasta_pacientes.glob("*/projeto/info.json"):
            try:
                # Usar context manager (with) é mais seguro para garantir o fechamento do arquivo
                with open(info_path, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                # Armazenamos a RAIZ do paciente (dois níveis acima de info.json)
                # Ex: pacientes/PRJ_ID_JOAO
                dados["_caminho_local"] = str(info_path.parent.parent)

                projetos.append(dados)
            except Exception as e:
                logging.error(f"Erro ao ler projeto em {info_path}: {e}")

        # Opcional: Ordenar por data de criação se o campo existir (mais recentes primeiro)
        try:
            projetos.sort(key=lambda x: x.get("data_criacao", ""), reverse=True)
        except:
            pass

        return projetos

    def listar_fluxos_disponiveis(self, ignorar_arquivo: str = None) -> List[Dict[str, Any]]:
        """Lê os templates de fluxo na pasta de fluxos."""
        fluxos = []
        if not self.pasta_fluxos.exists():
            return fluxos

        # Filtra apenas arquivos .json
        for path in self.pasta_fluxos.glob("*.json"):
            # Ignora o arquivo de cadastro se for passado (como 'cadastro_novo_paciente.json')
            if ignorar_arquivo and path.name == Path(ignorar_arquivo).name:
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    dados = json.load(f)

                dados["_caminho_arquivo"] = str(path)
                fluxos.append(dados)
            except Exception as e:
                logging.error(f"Erro ao ler fluxo em {path}: {e}")

        return fluxos

    def salvar_projeto(self, caminho_projeto: Path, dados: Dict[str, Any]):
        """
        Salva ou atualiza o info.json.
        caminho_projeto deve ser a raiz do paciente (ex: Path('pacientes/PRJ_001'))
        """
        try:
            caminho_projeto = Path(caminho_projeto)
            pasta_meta = caminho_projeto / "projeto"
            pasta_meta.mkdir(parents=True, exist_ok=True)

            arquivo_info = pasta_meta / "info.json"

            # Garante que o ID e o caminho estejam sincronizados se necessário
            with open(arquivo_info, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)

            logging.info(f"Projeto salvo com sucesso: {arquivo_info}")
        except Exception as e:
            logging.error(f"Falha ao salvar projeto em {caminho_projeto}: {e}")
            raise  # Lança o erro para a UI poder avisar o usuário