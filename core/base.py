from PySide6 import QtWidgets, QtCore

class ModuloBase(QtWidgets.QWidget):

    concluido = QtCore.Signal()     # Sinal disparado ao finalizar a tarefa do módulo

    def __init__(self):
        super().__init__()
        self.pasta_paciente = None

    def inicializar(self, caminho_paciente):

        self.pasta_paciente = caminho_paciente      # Define a pasta do paciente e prepara o módulo

    def verificar_pre_requisitos(self) -> tuple[bool, str]:
        # Valida arquivos necessários e retorna (Status, Mensagem)
        return True, ""

    def get_workspace(self) -> QtWidgets.QWidget:
        # Retorna a widget da área central
        return QtWidgets.QLabel("Área de Trabalho não implementada")

    def get_workspace_toolbar(self) -> QtWidgets.QWidget:
        # Retorna a barra de ferramentas da área central
        return QtWidgets.QLabel("Ferramentas de Trabalho")

    def get_toolbox(self) -> QtWidgets.QWidget:
        # Retorna o painel lateral de ferramentas
        return QtWidgets.QWidget()

    def validar_passagem(self) -> bool:
        # Verifica se as ações obrigatórias foram concluídas
        return True


class FluxoBase:
    def __init__(self, dados_json):
        # Mapeia os dados do JSON para o objeto
        self.nome = dados_json.get('nome', 'Fluxo Sem Nome')
        self.sequencia = dados_json.get('sequencia', [])
        self.cor_fundo = dados_json.get('cor_fundo', {})
        self.indice_atual = 0
        self.modo_avancado = False

    def get_modulo_atual_id(self):
        # Retorna o ID do módulo da etapa atual
        if self.sequencia and 0 <= self.indice_atual < len(self.sequencia):
            return self.sequencia[self.indice_atual]
        return None

    def avancar(self) -> bool:
        # Incrementa o índice para a próxima etapa
        if self.indice_atual < len(self.sequencia) - 1:
            self.indice_atual += 1
            return True
        return False

    def retroceder(self) -> bool:
        # Decrementa o índice para a etapa anterior
        if self.indice_atual > 0:
            self.indice_atual -= 1
            return True
        return False

    @property
    def esta_no_fim(self) -> bool:
        # Checa se é o último módulo
        return self.indice_atual == len(self.sequencia) - 1

    @property
    def esta_no_inicio(self) -> bool:
        # Checa se é o primeiro módulo
        return self.indice_atual == 0