# AGENTS.md - OpenCMF AI Coding Guide

OpenCMF is a modular surgical planning system for Craniomaxillofacial (CMF) surgery. This guide helps AI agents understand the architecture and contribute effectively.

## Architecture Overview

### Core Structure
- **`main.py`**: Entry point; initializes MainWindow with stacked widget navigation between Home, WorkspaceManager, FlowEditor, and SettingsPage
- **`core/base_module/base.py`**: `ModuloBase` (all surgical modules inherit this) and `FluxoBase` (workflow definition from JSON)
- **`core/workspace/`**: Manages multi-module workflow tabs with lazy-loading and signal-driven initialization
- **`modules/`**: Surgical operation modules (Registration, Tomography, Segmentation, Cephalometry, Patients)

### Data Flow Architecture
1. **Home Page** → Project selected → **WorkspaceManager** loads flow
2. **FluxoBase** (from `flows/*.json`) defines module sequence
3. **WorkspaceManager** creates tabs, lazy-loads `ModuloBase` subclasses on first view
4. **Each Module** initializes with `patient_path`, loads its workspace (central area) + toolbar + toolboxes
5. **ObjectManager** handles persistent object state per patient folder

### Key Coupling Points
- **PySide6 + VTK**: GUI uses Qt widgets; 3D rendering via `vtkmodules.qt.QVTKRenderWindowInteractor`
- **Signal-Slot Pattern**: All inter-component communication is Qt signals (e.g., `importRequested`, `objetoToggled`)
- **JSON Flows**: `flows/*.json` defines module sequences (e.g., `"sequencia": ["Paciente"]`)
- **Lazy Loading**: Modules instantiate only when user clicks their tab (WorkspaceManager._lazy_registry)

## Critical Developer Patterns

### Module Pattern (See `modules/_template_modulo.py`)
Every surgical module must:
```python
class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.nome = "Display Name"  # Tab label
    
    def inicializar(self, caminho_paciente: str) -> None:
        super().inicializar(caminho_paciente)  # Sets self.pasta_paciente
        # Load patient data here
    
    def get_workspace(self) -> QtWidgets.QWidget:
        # Central 3D/2D visualization area
    
    def get_workspace_toolbar(self) -> QtWidgets.QToolBar:
        # Toolbar above workspace
    
    def get_toolboxes(self) -> Dict[str, QtWidgets.QWidget]:
        # Side panels: {"Panel Name": widget, ...}
```

### Component Loading Pattern
- **Real Entry Point**: `modules/{module_name}.py` imports from `mod_{module_name}/controller.py`
  - Example: `tomography.py` → `from .mod_tomography.controller import Modulo`
  - This enables organized submodules while maintaining flat module discovery
- **ComponentLoader** scans `core/components/{toolbars,toolboxes,central_area}` for `Component` classes

### Localization Pattern
- **Singleton Translator**: `core/localization/translator.py` with i18n keys like `tr("home.recent_projects_title")`
- **Translation Files**: `core/localization/translations/{pt_BR,en_US}.json`
- **Settings-Driven**: Active language in `core/home_page/settings_app.py` (INI-based)

### VTK Rendering Pattern
- **Window Bases**: `core/components/central_area/base/janelas.py` (JanelaBase) handles:
  - `QVTKRenderWindowInteractor` initialization in `showEvent()` (critical!)
  - Interactor style setup (Image vs TrackballCamera)
  - Renderer background color
- **Object Management**: `adicionar_objeto()` creates vtkActor + vtkPolyDataMapper, stores in `atores_malha` dict
- **Multiple Views**: Registration uses `WindowRegistration` with dual 3D viewers (Side-by-side comparison pattern)

### Object Persistence Pattern
- **ObjectManager** (`core/imports/object_manager.py`): Stores ObjectProperties as JSON per patient
- **ObjectProperties** (`core/imports/models_import.py`): Dataclass with render, transform, visibility state
- **File Structure**: `patients/PRJ_{timestamp}_{name}/objects.json` + subfolders for models

## Building & Testing

### Run Application
```powershell
python main.py
```

### Pack Codebase (for AI context)
```powershell
python pack_code.py  # Generates contexto.txt with all .py and .ui files
```

### Key Configuration Files
- **`core/config.json`**: App metadata, theme preference, autosave settings
- **`core/home_page/settings_app.py`**: INI-based settings loader (theme, language)
- **`appearance/themes/*.qss`**: Qt stylesheets (dark, fusion, roxo, etc.)

## Important Patterns & Anti-Patterns

### ✅ DO:
- Use `ModuloBase` as superclass; inherit `inicializar()` and implement workspace getters
- Emit signals for UI events (`QtCore.Signal` typed, connected in parent)
- Store patient path in `self.pasta_paciente` (set by WorkspaceManager during tab init)
- Use `ObjectManager` for multi-object workflows (Registration, Segmentation)
- Load VTK components in `showEvent()` not `__init__()` (avoids initialization order issues)
- Organize large modules: `modules/mod_{name}/controller.py` + `view.py`, `toolbar.py`, etc.

### ❌ DON'T:
- Create VTK renderers/interactors outside JanelaBase hierarchy (breaks initialization)
- Import entire modules in `__init__.py` for discovery (causes circular imports); use dynamic loading
- Hardcode paths (use `get_resource_path()` for frozen app compatibility)
- Block UI with long computations (use `QtCore.QTimer.singleShot()` or threading)
- Skip `super().inicializar()` in module init (breaks patient path propagation)

## File Organization for New Features

### Add a New Surgical Module
1. Create `modules/mod_{name}/controller.py` with `class Modulo(ModuloBase)`
2. Create entry point `modules/{name}.py` → `from .mod_{name}.controller import Modulo`
3. Add tabs/components in `mod_{name}/view.py`, `toolbar.py`, `toolboxes.py`
4. Reference in `flows/*.json` sequence: `"sequencia": ["module_name", ...]`

### Add a New Toolbar
1. Create `core/components/toolbars/{feature}_toolbar.py`
2. Export `class Component(QtWidgets.QToolBar)` with `self.handler = HandlerClass(self)`
3. ComponentLoader auto-discovers; register in module's `get_workspace_toolbar()`

### Add Localization
1. Add key paths to `core/localization/translations/pt_BR.json` and others
2. Use `tr("section.key", default_text)` in code
3. Settings UI toggles language; Translator singleton reinitializes on change

## External Dependencies to Know
- **PySide6 6.11.0**: UI framework, signals/slots, layouts
- **VTK 9.6.1**: 3D rendering, mesh I/O (STL, OBJ, PLY), volume rendering
- **NumPy 2.4.4**: Data processing for volume operations
- **PyDICOM 3.0.2**: DICOM parsing for medical imaging
- **Nibabel 5.4.2**: NIfTI format support for brain/volume data

## Debugging Tips
- Enable VTK warnings: Remove `vtk.vtkObject.GlobalWarningDisplayOff()` from module init
- Check lazy-loading: WorkspaceManager._lazy_registry tracks module state
- Inspect signals: Add `.connect(lambda: print(...))` to trace flow
- Patient path survival: Confirm `self.pasta_paciente` set before `get_workspace()` call
- Theme issues: Verify stylesheet paths in `appearance/themes/` match QSS selectors

---

**Last Updated**: 2026-05-08  
**For Questions**: Review `core/base_module/base.py` for base class contracts; check `modules/registration.py` for complete module example.

