Anatomy/
│
├── __init__.py
├── entities/
│   ├── __init__.py
│   ├── mandible.py           # Objeto anatômico da Mandíbula (contém subpartes estáticas: ramos, corpo, côndilos, mento).
│   ├── maxilla.py            # Objeto anatômico da Maxila (referências anatômicas e plano oclusal estático).
│   ├── skull.py              # Malha craniofacial completa (arcabouço e base de referência óssea).
│   ├── facial_scan.py        # Superfície pura de tecidos moles da face (apenas armazena a malha estética).
│   ├── dental_model.py       # Modelos dentais digitais puros das arcadas superior e inferior.
│   └── surgical_guide.py     # Definição geométrica estática dos guias cirúrgicos.
│
├── osteotomies/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   └── osteotomy.py      # Definição base/abstrata das linhas e planos de corte ósseo.
│   ├── maxilla/
│   │   ├── __init__.py
│   │   ├── lefort1.py        # Padrão anatômico do corte Le Fort I.
│   │   ├── lefort2.py        # Padrão anatômico do corte Le Fort II.
│   │   └── lefort3.py        # Padrão anatômico do corte Le Fort III.
│   ├── mandible/
│   │   ├── __init__.py
│   │   ├── bsso.py           # Padrão anatômico da BSSO (Osteotomia Sagital).
│   │   ├── ivro.py           # Padrão anatômico da IVRO.
│   │   └── vertical.py       # Variações de cortes verticais do ramo.
│   └── chin/
│       ├── __init__.py
│       └── genioplasty.py    # Padrão anatômico do corte do mento.
│
├── landmarks/
│   ├── __init__.py
│   ├── cephalometric.py      # Mapeamento estático de pontos cefalométricos tradicionais (N, S, Me, Pog, etc.).
│   └── custom_points.py      # Gestão de pontos de referência anatômica personalizados.
│
├── measurements/
│   ├── __init__.py
│   ├── analysis.py           # Definição das fórmulas de análises cefalométricas e dimensionais.
│   ├── metrics.py            # Cálculo estático de distâncias lineares, angulares e assimetrias ósseas.
│   └── reports.py            # Estruturação de dados para relatórios métricos.
│
├── regions/
│   ├── __init__.py
│   ├── inferior_alveolar_canal.py # Mapeamento anatômico do canal do nervo alveolar inferior.
│   ├── condyle.py            # Delimitação estática da região anatômica condilar.
│   └── maxillary_sinus.py    # Delimitação anatômica dos seios maxilares.
│
└── occlusion/
    ├── __init__.py
    ├── arch.py               # Representação puramente anatômica/geométrica dos arcos dentários.
    ├── contacts.py           # Mapeamento estático de pontos de contato oclusal inicial.
    └── intermaxillary.py     # Definição estática da relação intermaxilar de referência.