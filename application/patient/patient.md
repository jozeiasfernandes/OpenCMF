# Fluxo de Dados do Paciente (OpenCMF)

Este documento descreve a arquitetura e o pipeline do fluxo de dados do paciente dentro da aplicação **OpenCMF**, detalhando o papel de cada componente desde a seleção inicial até a exibição e manipulação nos módulos de trabalho.

---

## 1. Visão Geral da Arquitetura

O sistema adota uma abordagem orientada a eventos e separação de responsabilidades, dividindo o fluxo em três camadas principais:
1. **Origem e Seleção (`Home_page` & `ProjectServiceHomePage`)**: Interface inicial de gerenciamento e persistência física em disco.
2. **Gerenciamento de Sessão (`PatientManager`)**: Núcleo reativo (Singleton) que mantém o estado global do paciente ativo e notifica os observadores.
3. **Coordenação e Execução (`MainWindow`, `Workspace` & Módulos)**: Camada de interface de trabalho que consome o estado e inicializa dinamicamente as ferramentas e abas do fluxo clínico.

---

## 2. O Fluxo de Dados Unificado passo a passo
1. Início na Home_page: O usuário interage com os serviços de projeto e fluxo para selecionar um paciente existente ou criar um novo. A seleção emite o caminho do projeto (patient_path) em conjunto com a escolha de um fluxo de trabalho.

2. Coordenação no main (MainWindow): A janela principal intercepta os sinais vindos da página inicial e delega a definição do paciente ativo para o PatientManager, que gerencia a sessão global e inicializa as dependências do fluxo por meio do ProjectServiceHomePage e da WorkspaceManager.

3. Gerenciamento na Workspace e Mixins (WorkspaceManager e WorkspacePatientMixin): A área de trabalho centraliza o estado global da sessão do paciente utilizando o WorkspaceState (que emite sinais reativos de mudança) e o WorkspacePatientMixin (responsável por verificar e propagar o caminho de forma segura).

4. Destino no Módulo (Module Patient): Por fim, a workspace localiza o módulo ativo correspondente e dispara o método de inicialização (modulo.inicializar(caminho_paciente)), fazendo com que o ProjectServiceHomePage carregue o arquivo info.json e popule as respectivas abas de dados, arquivos e projetos do paciente.
