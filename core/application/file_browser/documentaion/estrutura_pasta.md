core/
└── application/
    └── common/                          # Nova pasta para componentes reutilizáveis globais
        └── file_browser/                # Módulo dedicado ao explorador de arquivos
            ├── __init__.py
            ├── file_browser_view.py     # Widget principal da árvore e navegação
            ├── file_browser_dialog.py   # Wrapper de QDialog (caso precise abrir em janela modal flutuante)
            └── file_browser_controller.py # Lógica de filtros, atalhos do sistema e manipulação de diretórios