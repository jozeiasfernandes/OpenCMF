Geometry é o núcleo de computação gráfica e manipulação matemática pura do OpenCMF. Ela opera de forma totalmente agnóstica e desacoplada, o que significa que não possui conhecimento de conceitos clínicos, anatômicos ou cirúrgicos (como mandíbula, maxila ou osteotomias). O seu único propósito é gerenciar primitivas geométricas, algoritmos de processamento espacial, renderização visual, importação/exportação e adaptadores de comunicação.

Qualquer objeto ou ferramenta do sistema pode reutilizar esta engine geométrica para manipular malhas e dados espaciais.

Descrição Detalhada dos Módulos

## 1. geometry/ (Primitivas Espaciais)

Contém as classes fundamentais que representam os dados geométricos brutos em memória:mesh.py: A estrutura base para malhas poligonais de superfície (geralmente malhas triangulares), contendo arrays de vértices, faces, normais e conectividade topológica.point_cloud.py: Gerenciamento de conjuntos de pontos no espaço 3D sem conectividade de malha, ideal para processamento inicial de escaneamentos e nuvens de pontos densas.curve.py: Implementação de curvas paramétricas e splines espaciais utilizadas para marcação de trajetórias ou guias lineares.polyline.py: Sequências de segmentos de reta conectados, úteis para marcações abertas ou poligonais de corte.volume_mesh.py: Representação de malhas volumétricas (como elementos tetraédricos ou hexaédricos), fundamentais para simulações mecânicas avançadas.

## 2.algorithms/ (Processamento Geométrico Pesado)

Reúne os algoritmos matemáticos e computacionais aplicados sobre as primitivas:boolean/: Executa operações construtivas de sólidos (CSG), como união, subtração e intersecção entre malhas.repair/: Identifica e corrige problemas topológicos comuns em malhas digitais (buracos, arestas não-manifold, auto-intersecções e inversão de normais).remesh/: Algoritmos de reamalgamação e otimização da densidade e distribuição dos triângulos da malha.registration/: Métodos de alinhamento espacial de superfícies, destacando-se o algoritmo Iterative Closest Point (ICP) para fusão de dados.smoothing/: Técnicas de filtragem espacial para remoção de ruídos e suavização de superfícies poligonais.sculpt/: Deformações locais interativas baseadas em ferramentas de pincel para manipulação direta de vértices.measurements/: Rotinas para cálculo métrico de volume, área superficial, distâncias euclidianas e ângulos entre elementos.transforms/: Operações matriciais homogêneas ($4 \times 4$), controle de rotações, translações, escalas e mudanças de base espacial.

## 3. appearance/ (Aparência Visual)

Controla como as geometrias são estilizadas antes de atingirem a tela:material.py: Gerencia parâmetros de sombreamento, texturas e mapas visuais aplicados à superfície.render_properties.py: Controla opções de exibição como wireframe, transparência, opacidade e visibilidade de componentes.color.py: Manipulação de cores estáticas, gradientes de calor (heatmaps) e mapeamento de dados escalares em vértices.

## 4. selection/ (Seleção e Interação)

Gerencia a forma como o usuário interage e seleciona subpartes da geometria:selection.py: Gerenciamento de listas de elementos ativos (conjuntos de vértices, faces ou arestas selecionados).picking.py: Algoritmos de ray-casting e detecção de interseção para identificar qual objeto ou face o usuário clicou na tela.filters.py: Ferramentas para filtrar seleções com base em critérios geométricos restritos (limites de ângulo, área ou bounding boxes).

## 5. metadata/ (Metadados e Contexto Espacial)

Armazena informações descritivas e contextuais acopladas aos dados geométricos:acquisition.py: Registra dados sobre a origem, data e equipamento/método que gerou o arquivo geométrico.coordinate_system.py: Define matrizes de referência espacial e orientação de eixos (importante para manter o alinhamento anatômico original).tags.py: Sistema flexível de tags e anotações personalizadas em formato chave-valor.

## 6. io/ (Entrada e Saída de Dados)

Responsável pela persistência e conversão de arquivos geométricos:stl.py: Leitura e escrita de arquivos STL (Standard Triangle Language) em formatos binário e ASCII.obj.py: Importação e exportação de arquivos Wavefront OBJ com suporte a grupos e materiais associados.ply.py: Gerenciamento do formato PLY (Polygon File Format) com suporte a atributos por vértice (como cores e normais).importer.py: Orquestrador central que identifica o formato e direciona para o leitor adequado.exporter.py: Orquestrador central para exportação unificada de malhas processadas.7. adapters/ e scene/ (Camada de Integração)Garantem a comunicação limpa entre o motor matemático e o restante da aplicação:adapters/scene_adapter.py: Traduz estruturas de dados geométricos puros em buffers otimizados para a engine de renderização gráfica.adapters/tool_adapter.py: Fornece uma API padronizada e segura para que ferramentas externas modifiquem a geometria sem acoplamento direto.scene/scene_bridge.py: Atua como a ponte bidirecional entre o núcleo de geometria e a árvore de cena global da aplicação.