                    ┌─────────────────────┐
                    │  workspace_manager  │ ← IMPLEMENTAÇÃO ATIVA
                    │   (700+ linhas)     │
                    └─────────────────────┘
                               │
                               │ USADO
                               ▼
                    ┌─────────────────────┐
                    │  Side_Panel_Manager_Loaders   │
                    │  ComponentLoader    │
                    │  Components_List  
                    |│
                    └─────────────────────┘

                    ┌─────────────────────┐
                    │    manager.py       │ ← IMPLEMENTAÇÃO NOVA
                    │   (80 linhas)       │    (NÃO UTILIZADA)
                    └─────────────────────┘
                               │
                               │ DEPENDE
                               ▼
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   registry.py   │  │   layout.py     │  │   state.py      │
│  (implementado) │  │  (implementado) │  │   (VAZIO)       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                    │
          ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│   contracts.py  │  │   components/   │
│  (implementado) │  │   (parcial)     │
└─────────────────┘  └─────────────────┘



Workspace (Manager)
    ↓
TabController → Container (QStackedWidget)
    ↓
Module → LayoutBuilder → Splitter
    ↓                        ↓
Toolboxes (SidePanels)    Viewport (CentralArea)
    ↓                        ↓
ComponentLoader          ComponentLoader
    ↓                        ↓
Registry ← Scanner → Filesystem



1. A Hierarquia de Dependências
BaseComponent (A Fundamentação): É o único que conhece o scene_manager e detém a lógica de ciclo de vida (dispose, setup). Ele é o "fornecedor".

Componentes (Toolbar, SidePanel, CentralArea): Herdam de BaseComponent. Eles são os "consumidores" da lógica. Eles existem para servir ao usuário final e manipular o scene_manager conforme necessário.

ModuleBase (O Orquestrador): Não herda de BaseComponent. Ele é apenas o "container" que agrupa esses componentes. Ele recebe o contexto e atua como o distribuidor para seus filhos.

Workspace (O Layout Final): É o palco onde os módulos são exibidos. Ele é agnóstico à lógica interna dos módulos.

2. Fluxo de Dados (A "Harmonia")
Para que essa estrutura funcione sem que você precise "herdar de tudo", o fluxo de injeção de dependência deve ser assim:

ModuleFactory cria o Módulo passando o context (que contém o scene_manager).

O Módulo instancia seus Componentes, passando esse mesmo context para cada um deles.

Os Componentes (que herdam de BaseComponent) recebem o context, validam o scene_manager e ficam prontos para o uso.

3. Por que isso resolve seu desconforto?
O Módulo não "vira" um componente: Ele continua sendo uma QWidget simples (o que você queria). Ele não precisa de dispose() ou setup_component() porque ele delega essas tarefas para os componentes filhos que ele gerencia.

Centralização do scene_manager: Ele está confinado ao BaseComponent. Nenhum módulo ou workspace precisa saber que o VTK ou o motor gráfico existe; eles apenas interagem com os componentes que você criou.

Modularidade Total: Se você quiser trocar uma Toolbar por outra, você altera apenas a instância dentro do módulo. A Workspace nem percebe que a mudança aconteceu.

Resumo Visual
Plaintext
[AppContext] 
      │
      └─> [ModuleFactory]
               │
               └─> [Cephalometry_Module] ──> Repassa context
                        │
                        ├─> [Toolbar (BaseComponent)] ──> Acessa scene_manager
                        ├─> [SidePanel (BaseComponent)] ──> Acessa scene_manager
                        └─> [CentralArea (BaseComponent)] ──> Acessa scene_manager