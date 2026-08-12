core/
├── imports/
│   ├── __init__.py
│   ├── import_manager.py              # Classe principal do subsistema
│   ├── importer_registry.py           # Registro automático dos importadores
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── import_item.py
│   │   ├── import_category.py
│   │   ├── import_source.py
│   │   └── favorite_location.py
│   │
│   ├── importers/
│   │   ├── __init__.py
│   │   ├── base_importer.py
│   │   ├── dicom_importer.py
│   │   ├── volume_importer.py
│   │   ├── radiography_importer.py
│   │   ├── scan_importer.py
│   │   ├── photo_importer.py
│   │   ├── mesh_importer.py
│   │   ├── library_importer.py
│   │   ├── facial_implant_importer.py
│   │   └── dental_implant_importer.py
│   │
│   ├── browser/
│   │   ├── __init__.py
│   │   ├── file_browser.py            # OpenCMF File Browser
│   │   ├── file_model.py
│   │   ├── file_filters.py
│   │   ├── favorites_manager.py
│   │   ├── recent_manager.py
│   │   └── thumbnail_cache.py
│   │
│   ├── preview/
│   │   ├── __init__.py
│   │   ├── preview_manager.py
│   │   ├── volume_preview.py
│   │   ├── mesh_preview.py
│   │   ├── image_preview.py
│   │   └── object_preview.py
│   │
│   ├── metadata/
│   │   ├── __init__.py
│   │   ├── dicom_metadata.py
│   │   ├── mesh_metadata.py
│   │   ├── image_metadata.py
│   │   └── volume_metadata.py
│   │
│   ├── library/
│   │   ├── __init__.py
│   │   ├── library_manager.py
│   │   ├── library_item.py
│   │   ├── local_library.py
│   │   └── online_library.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py
│       └── path_utils.py
│
└── import_windows/
    └── import_manager/
        ├── __init__.py
        ├── import_window.py          # Janela principal (QSplitter triplo)
        ├── panels/
        │   ├── __init__.py
        │   ├── category_panel.py     # Painel 1: Árvore de categorias (QTreeWidget + tr)
        │   ├── source_panel.py       # Painel 2: Origem/Local (Do projeto, Do arquivo, Filtros)
        │   └── workspace_panel.py    # Painel 3: Área principal dividida verticalmente
        └── widgets/
            ├── __init__.py
            ├── item_card.py          # Cards visuais (Lista/Grid + seleções múltiplas)
            ├── slice_viewer.py       # Visualizador de fatias e metadados para volumes
            └── file_dialog_widget.py # Explorador de arquivos personalizado ("Do arquivo")