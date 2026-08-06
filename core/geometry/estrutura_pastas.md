Geometry/
│
├── geometry/
│   ├── __init__.py
│   ├── mesh.py             # Define a malha geométrica base (vértices, faces, normais e dados de topologia).
│   ├── point_cloud.py      # Gerencia estruturas de nuvens de pontos (usado em alinhamentos e escaneamentos brutos).
│   ├── curve.py            # Representa curvas espaciais e splines para marcações e guias lineares.
│   ├── polyline.py         # Gerencia sequências de segmentos de reta conectados no espaço 3D.
│   └── volume_mesh.py      # Define malhas volumétricas (tetraédricas/hexaédricas) para simulações e elementos finitos.
│
├── algorithms/
│   ├── __init__.py
│   ├── boolean/
│   │   ├── __init__.py
│   │   └── boolean_ops.py  # Executa operações booleanas (união, subtração e intersecção) entre malhas.
│   ├── repair/
│   │   ├── __init__.py
│   │   └── mesh_repair.py  # Corrige defeitos topológicos, buracos, malhas não-manifold e normais invertidas.
│   ├── remesh/
│   │   ├── __init__.py
│   │   └── remeshing.py    # Otimiza densidade de malhas e reconstrói topologia (remalhagem adaptativa).
│   ├── registration/
│   │   ├── __init__.py
│   │   └── icp.py          # Algoritmos de alinhamento espacial (ex: ICP para fusão de superfícies).
│   ├── smoothing/
│   │   ├── __init__.py
│   │   └── smooth.py       # Algoritmos de suavização e filtragem de ruído em superfícies 3D.
│   ├── sculpt/
│   │   ├── __init__.py
│   │   └── deform.py       # Funções de deformação local e edição interativa de malha por pincéis.
│   ├── measurements/
│   │   ├── __init__.py
│   │   └── metrics.py      # Cálculo de propriedades geométricas (volume, área de superfície, distância e ângulos).
│   └── transforms/
│       ├── __init__.py
│       └── matrix4x4.py    # Manipulação de matrizes de transformação homogênea, rotações e translações espaciais.
│
├── appearance/
│   ├── __init__.py
│   ├── material.py         # Gerencia propriedades de sombreamento, texturas e mapas visuais dos objetos.
│   ├── render_properties.py# Configura opções de exibição, transparência e visibilidade de faces/arestas.
│   └── color.py            # Manipulação de paletas de cores, gradientes e mapeamento de dados em vértices.
│
├── selection/
│   ├── __init__.py
│   ├── selection.py        # Gerencia listas e estados de subelementos selecionados (vértices, faces, arestas).
│   ├── picking.py          # Lógica de seleção por clique na tela (ray-casting e interseção com a geometria).
│   └── filters.py          # Filtros para seleção baseada em critérios geométricos (ângulo, área, bounding box).
│
├── metadata/
│   ├── __init__.py
│   ├── acquisition.py      # Armazena dados de origem, data e método de aquisição do arquivo geométrico.
│   ├── coordinate_system.py# Define sistemas de coordenadas espaciais, matrizes de referência e orientação anatômica.
│   └── tags.py             # Sistema de etiquetagem, anotações e metadados chave-valor customizados.
│
├── io/
│   ├── __init__.py
│   ├── stl.py              # Leitura e escrita de arquivos no formato padrão STL (binário e ASCII).
│   ├── obj.py              # Leitura e escrita de arquivos no formato Wavefront OBJ (com suporte a materiais).
│   ├── ply.py              # Leitura e escrita de arquivos no formato PLY (suporte a cores e dados em vértices).
│   ├── importer.py         # Orquestrador central de importação de diferentes formatos geométricos.
│   └── exporter.py         # Orquestrador central de exportação de malhas e dados processados.
│
├── adapters/
│   ├── __init__.py
│   ├── scene_adapter.py    # Traduz dados geométricos puros para os buffers visuais consumidos pela renderização.
│   └── tool_adapter.py     # Interface de comunicação desacoplada entre as ferramentas externas e o núcleo geométrico.
│
└── scene/
    ├── __init__.py
    └── scene_bridge.py     # Ponte de comunicação bidirecional entre o motor de geometria e a árvore de cena global.