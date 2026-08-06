Arquitetura do Padrão Command no OpenCMF
Este documento descreve o funcionamento, os fluxos e a implementação do padrão Command dentro da arquitetura do OpenCMF, focado no gerenciamento de histórico de ações (Undo/Redo) em memória.

## 1. Visão Geral
O padrão Command encapsula uma solicitação como um objeto, permitindo parametrizar clientes com diferentes solicitações, enfileirar ou registrar operações e dar suporte a operações reversíveis.

No OpenCMF, o sistema de comandos foi desenhado para ser leve, separando a lógica pesada de processamento (como leitura de arquivos DICOM ou pipelines de dados) das ações discretas que alteram o estado da cena.

## 2. Estrutura de Arquivos e Componentes Base
A estrutura de comandos reside no diretório de comandos da aplicação e é composta pelos seguintes elementos centrais:

    command.py: Define a classe abstrata base Command e os metadados do comando (CommandMetadata).
    
    command_manager.py: Gerencia as pilhas de execução, controlando o histórico de Undo e Redo com limite configurável.
    
    Comandos Concretos: Classes específicas para ações de domínio (ex: add_object_command, delete_object_command, move_command, rotate_command, scale_command, select_object_command, etc.).

#### A. Metadados do Comando (CommandMetadata)
Cada comando possui metadados integrados para rastreabilidade, contendo:
    
    id: Identificador único universal (UUID).
    
    created_at: Carimbo de data e hora da criação da instância.
    
    source: Origem opcional da ação.
    
    description: Descrição textual legível da operação.

#### B. Classe Abstrata Base (Command)
Define o contrato obrigatório que todo comando deve seguir:
    
    execute() -> bool: Executa a ação principal e retorna um booleano indicando o sucesso.
    
    undo() -> bool: Reverte os efeitos da execução.
    
    redo() -> bool: Refaz a ação (por padrão, chama novamente execute()).
    
    can_execute() -> bool / can_undo() -> bool: Validam se a ação pode ser executada ou desfeita no momento atual. 

## 3. Fluxo de Funcionamento
O fluxo de uma ação com suporte a histórico segue estas etapas:

Ação do Usuário / Ferramenta: O usuário interage com uma ferramenta (ex: manipulação de objetos ou inclusão de elementos). A ferramenta executa qualquer processamento pesado necessário em seu próprio escopo.

Instanciação do Comando: Uma vez que os dados estão prontos, a ferramenta instancia o comando de domínio correspondente (por exemplo, AddObjectCommand), passando as referências necessárias (como o SceneManager e os dados do objeto).

Despacho para o Gerenciador: A ferramenta envia o comando para o gerenciador central: command_manager.execute(command).

Execução e Empilhamento:

    O CommandManager valida se o comando pode ser executado (can_execute()).
    
    O método .execute() é chamado. Se for bem-sucedido, o comando é marcado como executado e empilhado na pilha de Undo.
    
    A pilha de Redo é limpa (clear()), pois uma nova ação quebra a linha temporal anterior de refazer.
    
    O histórico é aparado (trim) caso ultrapasse o limite máximo configurado (max_history).

sequenceDiagram
    Usuário->>Ferramenta: Ação
    Ferramenta->>Comando: Instancia
    Ferramenta->>CommandManager: execute(command)
    CommandManager->>Command: can_execute()
    CommandManager->>Command: execute()
    CommandManager->>CommandManager: Empilha em _undo_stack
    CommandManager->>CommandManager: Limpa _redo_stack

## 4. Gerenciamento em Memória
Atualmente, todo o histórico opera estritamente em memória RAM utilizando pilhas baseadas em listas do Python (_undo_stack e _redo_stack):

* Vantagens: Alta velocidade de resposta para operações de Undo/Redo em tempo real.

* Ciclo de Vida: O histórico é volátil; ou seja, ao fechar a aplicação, as pilhas de comandos são descartadas.



Documentação do Sistema de Comandos (Command Pattern) - OpenCMF
Esta documentação detalha a implementação, o fluxo e exemplos práticos de como utilizar o padrão Command integrado às ferramentas (Tools) e ao gerenciamento de estado no OpenCMF.

1. Visão Geral da Arquitetura
O sistema de comandos foi projetado para separar a lógica de execução e processamento (como leitura de arquivos pesados, parsers e regras de negócio) da lógica de reversibilidade (Undo/Redo).

As Ferramentas (BaseTool): Atuam como orquestradoras. Elas lidam com a interface, eventos do usuário e processamentos pesados (ex: abrir arquivos DICOM). No final do fluxo, elas instanciam e despacham um comando.

Os Comandos (Command): São objetos leves e atômicos de domínio (ex: AddObjectCommand, MoveCommand) que sabem apenas como aplicar (execute) e reverter (undo) modificações diretamente no SceneManager.

O Gerenciador (CommandManager): Controla as pilhas de histórico em memória, gerenciando limites, execuções, refazimentos e desfazimentos.

2. Componentes Base do Sistema
A. Classe Abstrata de Comando (command.py)
Todo comando concreto herda de Command e deve implementar obrigatoriamente os métodos execute e undo.

Python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

@dataclass(slots=True)
class CommandMetadata:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    description: Optional[str] = None

class Command(ABC):
    name = "command"

    def __init__(self):
        self.metadata = CommandMetadata()
        self.executed = False

    @abstractmethod
    def execute(self) -> bool:
        pass

    @abstractmethod
    def undo(self) -> bool:
        pass

    def redo(self) -> bool:
        return self.execute()

    def can_execute(self) -> bool:
        return True

    def can_undo(self) -> bool:
        return self.executed

    def mark_executed(self) -> None:
        self.executed = True

    def mark_undone(self) -> None:
        self.executed = False
B. Gerenciador de Comandos (command_manager.py)
Responsável por controlar o histórico de alterações.

Python
from typing import List, Optional
from core.commands.base.command import Command

class CommandManager:
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute(self, command: Command) -> bool:
        if not command.can_execute():
            return False
        
        success = command.execute()
        if not success:
            return False

        command.mark_executed()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._trim_history()
        return True

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        
        command = self._undo_stack.pop()
        success = command.undo()
        if not success:
            self._undo_stack.append(command)
            return False

        command.mark_undone()
        self._redo_stack.append(command)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        
        command = self._redo_stack.pop()
        success = command.redo()
        if not success:
            self._redo_stack.append(command)
            return False

        command.mark_executed()
        self._undo_stack.append(command)
        return True

    def _trim_history(self) -> None:
        if len(self._undo_stack) > self.max_history:
            overflow = len(self._undo_stack) - self.max_history
            del self._undo_stack[:overflow]
3. Exemplo Prático: Implementando um Comando Concreto
Abaixo está o exemplo de um comando de domínio genérico para adicionar um objeto (como um volume DICOM ou malha) à cena:

Python
from core.commands.base.command import Command

class AddObjectCommand(Command):
    name = "add_object"

    def __init__(self, scene_manager, object_id: str, object_data, description: str = "Adicionar Objeto"):
        super().__init__()
        self.scene_manager = scene_manager
        self.object_id = object_id
        self.object_data = object_data
        self.metadata.description = description

    def execute(self) -> bool:
        try:
            # Insere o objeto no gerenciador de cena
            self.scene_manager.add_object(self.object_id, self.object_data)
            return True
        except Exception as e:
            print(f"Erro ao executar comando de adição: {e}")
            return False

    def undo(self) -> bool:
        try:
            # Remove o objeto da cena para reverter a ação
            self.scene_manager.remove_object(self.object_id)
            return True
        except Exception as e:
            print(f"Erro ao desfazer comando de adição: {e}")
            return False
4. Exemplo Prático: Integração com uma Ferramenta (Tool)
As ferramentas encapsulam o fluxo pesado de dados e acionam o CommandManager. Veja como a LoadDicomTool interage com o sistema de comandos:

Python
class LoadDicomTool:
    def __init__(self, context):
        self.context = context  # Contém scene_manager, command_manager, event_bus, etc.

    def trigger(self):
        # 1. Etapa de UI / Arquivos Pesados (Fora do Command)
        folder_path = self.open_file_dialog()
        if not folder_path:
            return

        # 2. Processamento e parsing pesado do DICOM
        dicom_volume_data = self.process_heavy_dicom_files(folder_path)
        new_object_id = self.generate_unique_id()

        # 3. Instanciação do Comando leve de domínio
        command = AddObjectCommand(
            scene_manager=self.context.scene_manager,
            object_id=new_object_id,
            object_data=dicom_volume_data,
            description="Carregar Tomografia DICOM"
        )

        # 4. Despacho para o gerenciador central
        success = self.context.command_manager.execute(command)

        if success:
            print("Volume DICOM carregado e registrado no histórico com sucesso!")

    def open_file_dialog(self):
        # Lógica de interface para selecionar pasta
        return "/path/to/dicom/files"

    def process_heavy_dicom_files(self, path):
        # Simula o pipeline de leitura e conversão para o VTK
        return {"data": "vtk_volume_object"}

    def generate_unique_id(self):
        import uuid
        return str(uuid.uuid4())
5. Resumo do Fluxo de Execução
Ação: O usuário aciona uma ferramenta na interface (ex: LoadDicomTool).

Processamento: A ferramenta executa o trabalho pesado de I/O, validação e parsing dos dados em seu próprio escopo.

Criação: A ferramenta cria a instância do comando (ex: AddObjectCommand) repassando apenas os dados já processados e a referência do SceneManager.

Execução: A ferramenta invoca command_manager.execute(command).

Histórico e Reação: O gerenciador executa o comando, aplica a alteração no SceneManager, empilha a ação para suporte a Undo/Redo, e o EventBus notifica a CentralAreaBase e o SidePanel para atualizarem a renderização visual e a árvore de objetos.