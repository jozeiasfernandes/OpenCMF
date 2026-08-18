domain/
└── osteosynthesis/
    ├── models/
    │   ├── plate.py
    │   ├── plate_element.py
    │   ├── connection.py
    │   ├── hole.py
    │   ├── screw.py
    │   ├── material.py
    │   └── plate_preset.py
    │
    ├── catalog/
    │   ├── plate_system.py
    │   ├── hole_specification.py
    │   ├── screw_specification.py
    │   └── material_catalog.py
    │
    ├── geometry/
    │   ├── plate_geometry.py
    │   ├── element_geometry.py
    │   ├── hole_geometry.py
    │   ├── screw_geometry.py
    │   ├── bend.py
    │   └── twist.py
    │
    └── validation/
        └── plate_validator.py
application/
└── osteosynthesis/
    ├── commands/
    │   ├── add_element.py
    │   ├── delete_element.py
    │   ├── add_hole.py
    │   ├── remove_hole.py
    │   ├── connect.py
    │   ├── disconnect.py
    │   ├── bend.py
    │   └── twist.py
    │
    ├── services/
    │   ├── plate_service.py
    │   ├── geometry_service.py
    │   ├── validation_service.py
    │   └── preset_service.py
    │
    └── state/
        └── osteosynthesis_state.py
infrastructure/
└── geometry/
    └── occt/
        ├── shape_builder.py
        ├── boolean_operations.py
        ├── tessellator.py
        └── converters.py
ui/
└── osteosynthesis/
    ├── tools/
    │   ├── create_plate.py
    │   ├── select.py
    │   ├── add_element.py
    │   ├── connect.py
    │   ├── bend.py
    │   └── twist.py
    │
    ├── dialogs/
    │   └── plate_configuration.py
    │
    ├── editors/
    │   ├── plate_editor.py
    │   ├── element_editor.py
    │   └── connection_editor.py
    │
    ├── widgets/
    │   ├── property_editor.py
    │   ├── element_table.py
    │   ├── preset_selector.py
    │   └── plate_preview.py
    │
    └── viewport/
        ├── plate_actor.py
        ├── screw_actor.py
        ├── selection_manager.py
        └── gizmos.py