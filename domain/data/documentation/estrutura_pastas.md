datatypes/
├── __init__.py
├── base.py                 # Fase 1: Classe base do Object (id, name, metadata, serialização)
├── registry.py             # Fase 3: DataTypeRegistry (gerenciamento e identificadores estáveis)
├── primitives/             # Tipos fundamentais e primitivos de dados
│   ├── __init__.py
│   ├── mesh.py             # Definição do tipo Mesh
│   ├── volume.py           # Definição do tipo Volume
│   ├── image2d.py          # Definição do tipo Image2D
│   ├── point.py            # Definição do tipo Point (Landmarks, etc.)
│   ├── curve.py            # Definição de Curvas (Splines, Bézier, Linhas)
│   └── pointcloud.py       # Definição de PointCloud
└── exceptions.py           # Erros customizados (ex: DataTypeNotFoundError, DuplicateObjectError)




OpenCMF/
│
├── domain/
│   │
│   ├── objects/
│   │   ├── base.py
│   │   └── metadata.py
│   │
│   ├── datatypes/
│   │   ├── mesh.py
│   │   ├── volume.py
│   │   ├── image_2d.py
│   │   ├── curve.py
│   │   ├── point.py
│   │   └── roi.py
│   │
│   ├── object_features/
│   │   ├── transform_feature.py
│   │   ├── render_feature.py
│   │   ├── mesh_feature.py
│   │   ├── volume_feature.py
│   │   ├── image_feature.py
│   │   └── surgical_feature.py
│   │
│   ├── semantics/
│   │   ├── registry.py
│   │   └── definitions.py
│   │
│   ├── capabilities/
│   │   ├── registry.py
│   │   └── definitions.py
│   │
│   ├── relationships/
│   │   ├── graph.py
│   │   └── types.py
│   │
│   └── object_system/
│       ├── registry.py
│       ├── factory.py
│       └── type_registry.py


