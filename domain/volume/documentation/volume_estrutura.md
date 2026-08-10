core/
└── volume/
    ├── models/                           # Modelos de dados
    │   ├── volume.py
    │   ├── mask.py
    │   ├── series.py
    │   └── __init__.py
    │
    ├── reference/                        # Dados de referência e atlas anatômicos
    │   ├── atlases.py
    │   ├── templates.py
    │   └── __init__.py
    │
    ├── dicom/                            # [Camada 0] Entrada
    │   ├── engines/
    │   │   ├── dicom_engine.py
    │   │   └── interfaces.py
    │   ├── validators/
    │   │   └── dicom_validator.py
    │   └── __init__.py
    │
    ├── preprocessing/                    # Volume → Volume
    │   ├── resample.py
    │   ├── normalize.py
    │   ├── denoise.py
    │   └── __init__.py
    │
    ├── registration/                     # Alinhamento espacial de volumes
    │   ├── rigid.py
    │   ├── affine.py
    │   └── __init__.py
    │
    ├── segmentation/                     # [Camada 2] Extração e Isolamento
    │   ├── engines/                      # Motores de segmentação por algoritmo/biblioteca
    |   |   |── Threshold
    │   │   ├── total_segmentator.py
    │   │   ├── dental_segmentator.py
    │   │   ├── amasss.py
    │   │   ├── monai_engine.py
    │   │   ├── manual.py
    │   │   └── __init__.py
    │   ├── strategies/                   # Algoritmos matemáticos de baixo nível (VTK/ITK)
    │   │   ├── threshold.py
    │   │   ├── region_growing.py
    │   │   └── __init__.py
    │   ├── operations/                   # Operações sobre máscaras
    │   │   ├── boolean.py
    │   │   ├── morphological.py
    │   │   ├── connectivity.py
    │   │   └── __init__.py
    │   ├── validators/
    │   │   ├── topology.py
    │   │   └── __init__.py
    │   └── __init__.py
    │
    ├── processing/                       # [Camada 2] Derivação
    │   ├── panoramic_reconstruction.py
    │   ├── mip.py
    │   ├── surface_extraction.py
    │   └── __init__.py
    │
    ├── analysis/                         # [Camada 3] Interpretação
    │   ├── measurements.py
    │   ├── density.py
    │   ├── histogram.py
    │   ├── shape_analysis.py
    │   └── __init__.py
    │
    ├── exporters/
    │   ├── __init__.py
    │   ├── volume_exporter.py
    │
    ├── visualization/                    # Recursos visuais e gerenciamento de cores
    |   ├── volume_viewer_widget.py
    │   ├── lut/                          # Gerenciamento de cores e paletas
    │   │   ├── manager.py                # Apenas lógica VTK (vtkLookupTable)
    │   │   ├── presets.py                # Dicionário de cores + renderização de ícones (PySide6)
    │   │   └── __init__.py
    |   └── presets/
    |       ├── lung.json        # Exemplo para pulmão (Hounsfield baixo)
    |       ├── bone.json        # Exemplo para ossos (Hounsfield alto)
    |       └── soft_tissue.json # Exemplo para tecidos moles
    │   ├── color_maps.py
    │   ├── annotations.py
    │   └── __init__.py
    │
    └── utils/                            # Utilitários globais de voxels/arrays (sem acoplamento gráfico)
        ├── geometry.py
        ├── array_utils.py
        └── __init__.py