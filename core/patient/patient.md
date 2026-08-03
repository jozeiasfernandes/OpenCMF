Fluxo de Dados do Paciente (OpenCMF)
Este documento descreve a arquitetura e o pipeline do fluxo de dados do paciente dentro da aplicação OpenCMF, detalhando o papel de cada componente desde a seleção inicial até a exibição e manipulação nos módulos de trabalho.

1. Visão Geral da Arquitetura
O sistema adota uma abordagem orientada a eventos e separação de responsabilidades, dividindo o fluxo em três camadas principais:

Origem e Seleção (Home_page & ProjectServiceHomePage): Interface inicial de gerenciamento e persistência física em disco.

Gerenciamento de Sessão (PatientManager): Núcleo reativo (Singleton) que mantém o estado global do paciente ativo e notifica os observadores.

Coordenação e Execução (MainWindow, Workspace & Módulos): Camada de interface de trabalho que consome o estado e inicializa dinamicamente as ferramentas e abas do fluxo clínico.

2. Passo a Passo do Fluxo de Dados
Snippet de código
sequenceDiagram
    participant Home as Home_page
    participant Service as ProjectServiceHomePage
    participant Manager as PatientManager
    participant Main as MainWindow
    participant WS as WorkspaceManager
    participant Mod as Módulo Ativo

    Home->>Manager: Seleciona projeto (path)
    Manager->>Service: load_project(root_path)
    Service-->>Manager: Retorna dados do info.json
    Manager-->>Main: Emite sinal (patient_changed & patient_data_loaded)
    Main->>WS: set_patient_path(current_path)
    WS->>Mod: modulo.inicializar(current_path)
    Mod->>Service: Lê arquivos e preenche abas/interface
Passo 1: Seleção do Projeto (Home_page)
O usuário interage com a página inicial (Home_page) escolhendo um paciente existente ou criando um novo.

O evento emite o caminho absoluto do diretório do paciente (patient_path) e o fluxo de trabalho escolhido.

Passo 2: Centralização de Sessão (PatientManager)
A MainWindow delega a seleção para o PatientManager (core.patient.patient_manager).

O PatientManager aciona o ProjectServiceHomePage para ler o arquivo info.json dentro da subpasta project/ e sincronizar os caminhos físicos dos diretórios de dados (volume, surfaces, photos, others).

O PatientManager emite dois sinais globais baseados em PySide6:

patient_changed(str): Transmite o novo caminho absoluto do paciente.

patient_data_loaded(dict): Transmite o dicionário completo de dados cadastrais e clínicos.

Passo 3: Inicialização do Workflow e Módulos (MainWindow & Workspace)
Com o caminho definido no gerenciador, a MainWindow carrega o arquivo de configuração do fluxo (ex: workflow.json) através da classe FluxoBase.

O WorkspaceManager é resetado e as classes dos módulos descritas no fluxo são registradas dinamicamente na ModuleFactory.

O WorkspaceManager exibe os módulos em abas na interface gráfica (TabController).

Passo 4: Sincronização Final com o Módulo (Module Patient)
O primeiro módulo ativo da pilha é acionado.

Através do método de inicialização (modulo.inicializar(path)), o módulo recebe o caminho do paciente e utiliza o ProjectServiceHomePage ou o contexto para popular suas respectivas abas, visualizadores 3D (DICOM/Superfícies) e campos de dados clínicos.