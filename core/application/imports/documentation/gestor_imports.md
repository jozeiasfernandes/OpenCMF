Plano de Construção da Janela do Gestor de Importações

## 1. Arquitetura Geral de Layout (3 Painéis com QSplitter)

Janela Principal (ImportManagerWindow): Baseada em um divisor horizontal principal (QSplitter), dividindo a interface em três painéis redimensionáveis e modulares.

* Painel 1 (Esquerda - Categorias): Árvore de navegação hierárquica usando QTreeWidget, contendo as categorias principais (Volume, Radiografias, Escaneamentos, Fotografias, Malhas 3D, Implantes Dentários, Implantes Faciais) e suas respectivas subcategorias.

* Painel 2 (Centro - Origem / Filtro de Contexto): Exibe as opções de origem ou os grupos de biblioteca dependendo da subcategoria selecionada no Painel 1 (ex: Do projeto vs. Do arquivo, ou classificações como Anatomia, Primitivos).

* Painel 3 (Direita - Workspace / Conteúdo Principal): Dividido verticalmente em duas seções por um QSplitter:

    Seção Superior: Exibe a listagem de itens (modo lista ou grid) ou o diálogo personalizado de arquivos locais, além de filtros por ComboBox e botões de visualização.

    Seção Inferior: Painel de pré-visualização (Preview) adaptativo (com controles de navegação por slices para volumes, visualização estática para imagens/radiografias, ou metadados detalhados) e o botão principal de Importar.

## 2. Mapeamento de Componentes por Módulo

### CategoryPanel (Painel 1):

Implementado com QTreeWidget.

Cliques em categorias principais realizam apenas a ação de expandir/recolher.

Cliques em subcategorias emitem um sinal personalizado (sub_category_selected) para atualizar o Painel 2.

Suporte nativo a internacionalização de textos.

### SourcePanel (Painel 2):

Dinâmico com base na seleção do Painel 1.

Para dados do projeto/arquivos: exibe opções como Do projeto e Do arquivo.

Para bibliotecas 3D e implantes: exibe filtros de catálogo (ex: Anatomia, Letras, Primitivos).

### WorkspacePanel (Painel 3):

#### Subseção Superior:

Alternância de layout entre Lista (menu.svg) e Grid (grid.svg).

Filtro avançado via ComboBox (ex: tipos de fotografia ou subgrupos de malhas).

Suporte a seleção múltipla através de caixas de seleção nos cartões.

Embutimento de explorador de arquivos personalizado quando a opção "Do arquivo" for selecionada.

#### Subseção Inferior:

Visualizador de Volumes: Informações técnicas do exame associadas a um painel gráfico com barra de rolagem horizontal (slider) para percorrer as fatias (slices).

Visualizador de Imagens/2D: Dados descritivos e preview estático para radiografias e fotografias.

Botão de validação e confirmação Importar.

## 3. Fases de Desenvolvimento Sugeridas

* Fase 1: Construção do esqueleto da janela principal com o QSplitter triplo e estruturação dos stubs para os três painéis.

* Fase 2: Implementação do Painel 1 (QTreeWidget) com suporte a ícones de expansão e sinais de navegação.

* Fase 3: Desenvolvimento do Painel 2 para alternar dinamicamente os seletores de origem e filtros de catálogo.

* Fase 4: Desenvolvimento do Painel 3 (Seção Superior), implementando a alternância entre os modos Grid/Lista e o carregamento de cartões de itens.

* Fase 5: Implementação do Painel 3 (Seção Inferior), integrando o painel de metadados, o visualizador de fatias (slices) e a lógica de validação do botão Importar.



