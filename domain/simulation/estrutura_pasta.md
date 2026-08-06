Simulation/
│
├── __init__.py
│
├── soft_tissue/                  # Simulação, deformação e predição estética cutânea
│   ├── __init__.py
│   ├── predictor.py              # Interface base/abstrata para modelos de predição de tecidos moles.
│   ├── laplacian_deformation.py  # Algoritmo de deformação cutânea baseado em coordenadas laplacianas.
│   ├── fem_predictor.py          # Simulação de tecidos moles usando Elementos Finitos (FEM).
│   └── rbf_predictor.py          # Deformação cutânea baseada em funções de base radial (RBF).
│
├── physics/                      # Biomecânica, física de materiais e dinâmica estrutural
│   ├── __init__.py
│   ├── tmj_dynamics.py           # Simulação da biomecânica e rotação condilar na articulação temporomandibular.
│   ├── bone_stress.py            # Estimativa de tensão e estresse mecânico em fixações e placas ósseas.
│   └── distraction.py            # Simulação física de distração osteogênica ao longo do tempo.
│
├── collision/                    # Detecção e tratamento de colisões e interseções espaciais
│   ├── __init__.py
│   ├── bone_collision.py         # Detecta interpenetração indesejada entre segmentos ósseos pós-osteotomia.
│   └── dental_collision.py       # Valida intersecções entre coroas e raízes dentárias.
│
├── constraints/                  # Resolução de limites e restrições espaciais dinâmicas
│   ├── __init__.py
│   ├── base_constraint.py        # Classe base/abstrata para todas as restrições ativas de movimento.
│   ├── occlusion_constraint.py   # Restringe o movimento intermaxilar para guiar a oclusão correta.
│   ├── tmj_constraint.py         # Limita o deslocamento do côndilo dentro dos limites fisiológicos da fossa.
│   ├── bone_contact_constraint.py# Valida a área mínima de contato ósseo para consolidação pós-corte.
│   └── dental_constraint.py      # Impede angulações extremas de raízes em relação a osteotomias.
│
├── prediction/                   # Modelos estatísticos, aprendizado de máquina e IA preditiva
│   ├── __init__.py
│   ├── statistical_model.py      # Modelos de forma estatística (SSM) para predição anatômica.
│   └── ai_predictor.py           # Integração com modelos de Inteligência Artificial para planejamento automatizado.
│
└── behaviors/                    # Orquestradores de regras cinemáticas e lógicas de planejamento cirúrgico
    ├── __init__.py
    ├── orthognathic_behavior.py  # Regras de movimentação bimaxilar acoplada (maxila + mandíbula).
    ├── implant_behavior.py       # Lógica de posicionamento guiado de implantes ortopédicos/dentários.
    └── plastic_behavior.py       # Comportamento conjunto de ajustes estéticos e esqueléticos.