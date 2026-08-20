O ThemeManager é o componente responsável por gerenciar e aplicar temas estáticos modulares e customizações dinâmicas de cores na aplicação PySide6. Sua principal responsabilidade é separar a estrutura/layout (gerenciada por arquivos de componentes) da identidade visual/cores (gerenciada por arquivos de temas ou painéis de customização).

## Visão Geral da Arquitetura
A arquitetura de temas adota uma abordagem modular baseada em duas camadas principais:

1. Camada Estrutural (components/): Localizada em diretórios dedicados (THEMES_COMPONENTS_DIR), armazena arquivos .qss focados exclusivamente em propriedades de layout, dimensões, fontes e espaçamentos (ex: border-radius, padding, min-height), sem conter definições de cores.
2.Camada de Cores (list_themes/): Contém arquivos de temas estáticos (ex: atom.qss) e o mecanismo de temas dinâmicos, definindo exclusivamente propriedades cromáticas (background-color, color, border-color).

## Métodos Principais
__init__(self, app: QtWidgets.QApplication)
Inicializa o gerenciador recebendo a instância principal da aplicação PySide6 (QApplication), permitindo a aplicação global de folhas de estilo.

apply_static_theme(self, theme_name: str) -> bool
Carrega e aplica um tema estático modular com base no nome fornecido.

## Funcionamento:

1. Varre a pasta de componentes estruturais e lê os arquivos essenciais (base.qss, buttons.qss, scrollbar.qss, workspace.qss, cards.qss).
2. Carrega o arquivo de cores correspondente localizado na raiz dos temas ({theme_name}.qss). 
3. Une todas as partes em uma única folha de estilo e a aplica globalmente na aplicação. 
4. Retorno: True se o tema foi aplicado com sucesso; False caso ocorra algum erro.

    get_user_customizations(self) -> dict
Retorna um dicionário contendo as cores customizadas pelo usuário salvas nas configurações da aplicação (settings). Caso nenhuma customização prévia exista, retorna uma paleta padrão de fallback.

    apply_custom_theme(self) -> bool
Lê um template dinâmico (dynamic_template.qss), substitui as variáveis de cores pelos valores definidos pelo usuário (obtidos via get_user_customizations()) e aplica o estilo resultante à aplicação.

    save_custom_color(self, key: str, hex_value: str) -> None
Atualiza o valor de uma cor específica nas preferências do usuário, persiste as alterações utilizando o gerenciador de configurações (settings) e reaplica imediatamente o tema customizado.

## Exemplo de Utilização
    Python
    from PySide6 import QtWidgets
    from core.settings.theme_manager import ThemeManager
    
    app = QtWidgets.QApplication([])
    theme_mgr = ThemeManager(app)
    
    # Aplicar um tema estático modular (ex: "atom")
    theme_mgr.apply_static_theme("atom")
    
    # Salvar e aplicar uma nova cor customizada dinamicamente
    theme_mgr.save_custom_color("accent_color", "#528bff")