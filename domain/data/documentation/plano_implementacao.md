## Fase 0 — Definir os contratos fundamentais

Antes de criar qualquer sistema, definir as entidades conceituais:

    BaseObject
    DataType
    ObjectFeature
    SemanticType
    Capability
    Relationship

A arquitetura conceitual:

    BaseObject
    │
    ├── identity
    ├── data
    ├── semantic
    ├── features
    ├── metadata
    └── properties

E:

    DataType
        → estrutura do dado
    
    
    Semantic
        → significado do dado
    
    
    Feature
        → característica presente no objeto
    
    
    Capability
        → operação permitida
    
    
    Relationship
        → relação com outro objeto

Essa fase é pequena, mas extremamente importante.


## Fase 1 — Criar o Object base

Portanto:

    BaseObject
    ├── id
    ├── name
    ├── data
    ├── semantic
    ├── metadata
    ├── features
    └── properties

Inicialmente:

    object.id
    object.name
    object.data_type
    object.semantic_type
    object.metadata

Nada de VTK, DICOM, UI ou algoritmos.

Objetivo: conseguir criar um objeto de domínio válido em memória.

## Fase 2 — DataTypes

Criar:

    domain/datatypes/
    ├── mesh.py
    ├── volume.py
    ├── image_2d.py
    ├── curve.py
    ├── point.py
    ├── pointcloud.py
    └── roi.py

E estabelecer identificadores estáveis:

    geometry.mesh
    volume
    image.2d
    geometry.curve
    geometry.point
    geometry.pointcloud
    geometry.roi
Por quê antes do Registry?

Porque primeiro precisamos definir o que é um DataType.

Depois registramos esses tipos.

## Fase 3 — DataTypeRegistry

Agora:

DataTypeRegistry

Responsável por:

    register()
    get()
    exists()
    all()

E:

    registry.get("geometry.mesh")

retorna a definição do tipo.

## Fase 4 — ObjectRegistry

Aqui entra seu Registry global.

    ObjectRegistry

Responsabilidades:

    register()
    unregister()
    get()
    exists()
    all()
    find_by_type()
    find_by_semantic()
    clear()

Uma distinção importante:

### DataTypeRegistry

    "Quais tipos o OpenCMF conhece?"

### ObjectRegistry

## Fase 5 — ObjectFactory

"Quais objetos existem nesta cena?"

Essa separação está excelente no seu plano original e deve ser preservada.

    ObjectFactory

Agora sim:

ObjectFactory

Fluxo:

    DataType
       ↓
    ObjectFactory
       ↓
    BaseObject

Métodos:

    create()
    create_from_data()
    clone()
    deserialize()

Ainda sem importadores.

Podemos testar:

    mesh = factory.create("geometry.mesh")

e obter:

    BaseObject
        type = geometry.mesh


## Fase 6 — Semântica

### SemanticRegistrystry

E a taxonomia:

    anatomy.bone.mandible
    anatomy.bone.maxilla
    anatomy.bone.skull


    anatomy.tooth
    
    
    anatomy.soft_tissue.nose
    anatomy.soft_tissue.lip
    
    
    radiography.panoramic
    
    
    implant.plate
    implant.screw
    implant.surgical_guide

Importante:

Semantic não precisa ser uma classe Python.

Pode ser uma definição declarativa.


## Fase 7 — Object Features

Aqui está a principal alteração em relação ao seu plano original.

Você chamou anteriormente de:

    ComponentRegistry
    
    Eu agora usaria:
    
    object_features/

e:

    FeatureRegistry

ou, se quisermos manter a infraestrutura junto do sistema:

    object_system/
    └── feature_registry.py

Os primeiros Features poderiam ser:

    TransformFeature
    RenderableFeature
    MeshFeature
    VolumeFeature
    ImageFeature
    LandmarkFeature
    MeasurementFeature
    AnnotationFeature
    SurgicalFeature
E aqui há uma regra importante:

Feature não é Capability.

Exemplo:

    Mandible
    │
    ├── MeshFeature
    ├── TransformFeature
    └── RenderFeature

significa:

A mandíbula possui esses recursos estruturais.

Enquanto:

    Capabilities
    ├── Transform
    ├── Boolean
    ├── Cut
    ├── Measure
    └── Osteotomy

significa:

Essas operações podem ser executadas sobre ela.

## Fase 8 — SceneGraph

Agora podemos implementar:

SceneGraph

com:

    SceneNode
    ├── object_id
    ├── parent_id
    ├── children
    └── local_transform

E:

    WorldTransform =
    ParentWorldTransform × LocalTransform

Seu teste da mandíbula continua perfeito:

    Mandible
    ├── Ramus R
    ├── Ramus L
    └── Body
        ├── Teeth
        └── Chin

Mover a mandíbula → todos acompanham.

Mover o mento → somente o ramo correspondente da hierarquia acompanha.

## Fase 8 — Transform System

Transform System

Aqui eu faria uma pequena alteração.

O TransformFeature contém o estado:

    position
    rotation
    scale
    matrix

O TransformSystem contém a lógica:

    calculate_local()
    calculate_world()
    update_hierarchy()
    apply_transform()

Isso mantém estado e algoritmo separados.

## Fase 9 — ComponentRegistry

Agora introduzimos componentes.

Primeiros componentes:

    TransformComponent
    RenderableComponent
    MeshComponent
    VolumeComponent
    Image2DComponent
    LandmarkComponent
    MeasurementComponent
    AnnotationComponent

Exemplo:

    Mandible
    │
    ├── MeshComponent
    ├── TransformComponent
    ├── RenderableComponent
    └── AnatomicalComponent

Enquanto:

    Panoramic
    │
    ├── Image2DComponent
    ├── Transform2DComponent
    └── Renderable2DComponent

Isso começa a produzir a diferenciação que você deseja.

## Fase 10 — Capability System

Agora sim:

    CapabilityRegistry

Primeiro:

    Select
    Delete
    Duplicate
    Visibility
    Transform
    Measure

Depois:

    Boolean
    Cut
    Remesh
    Segment
    Registration
    Osteotomy

E capacidades específicas para imagem:

    BrightnessContrast
    Crop
    Rotate2D
    Flip
    Annotate
    Export
    ExternalEditor

A lógica passa a ser:

    object.has_capability("geometry.boolean")

e não:

    if object.semantic == "mandible":

Esse é um dos maiores ganhos arquiteturais.

## Fase 11 — EventBus

Eu moveria o EventBus para antes do RelationshipGraph.

Criar:

    events/
    ├── event.py
    ├── bus.py
    └── types.py

Eventos iniciais:

    ObjectCreated
    ObjectDeleted
    ObjectSelected
    ObjectTransformed
    ObjectSemanticChanged
    FeatureAdded
    FeatureRemoved
    GeometryChanged
    RelationshipChanged

Agora os sistemas conseguem reagir sem depender diretamente uns dos outros.

## Fase 12 — RelationshipGraph

Só agora.

    relationships/
    ├── graph.py
    └── types.py

Relações:

    parent_of
    part_of
    attached_to
    depends_on
    derived_from
    references
    associated_with

Exemplo:

    Plate
       attached_to
          Mandible

ou:

    Measurement
       depends_on
          Landmark A
          Landmark B

E o EventBus permite:

    Mandible transformed
            ↓
         EventBus
            ↓
    RelationshipGraph
            ↓
       dependent objects
    Fase 13 — UI dinâmica

Agora sim a interface pode consumir o sistema.

O princípio:

    Object
       ↓
    Semantic
       +
    Features
         +
    Capabilities
       ↓
    Property Panel

Assim, selecionar:

Mandíbula

pode gerar:

    Transform
    Appearance
    Anatomy
    Landmarks
    Measurements
    Osteotomy
    Symmetry
    Surgical Planning
    Panorâmica

pode gerar:

    Brightness
    Contrast
    Zoom
    Rotation
    Annotation
    Landmark
    Export
    External Editor

Sem a UI precisar conhecer todos os tipos concretos.

## Fase 14 — Importers

Agora conectar seu sistema de importação existente.

Eu mudaria ligeiramente o fluxo que você escreveu.

Não seria:

    Importer
     ↓
    Raw Data
     ↓
    ObjectFactory
     ↓
    Object
     ↓
    DataTypeRegistry

O Importer já deve saber qual DataType produz.

Melhor:

    File
     ↓
    Importer
     ↓
    Data
     ↓
    ObjectFactory
     ↓
    BaseObject
     ↓
    DataType
     ↓
    Semantic Assignment
     ↓
    Features
     ↓
    Capabilities
     ↓
    ObjectRegistry
     ↓
    SceneGraph
    
    Exemplo:
    
    mandible.stl
         ↓
    STLImporter
         ↓
    MeshData
         ↓
    ObjectFactory
         ↓
    BaseObject
         ↓
    geometry.mesh
         ↓
    User assigns:
    anatomy.bone.mandible
         ↓
    Features + Capabilities

Isso mantém o Importer responsável por formato, e não por significado clínico.

## Fase 15 — Persistência

Eu manteria sua ideia de deixar JSON para depois.

Mas faria uma distinção:

    Project
    │
    ├── objects
    ├── scene
    ├── relationships
    ├── metadata
    └── resources

Um objeto:

    {
        "id": "uuid",
        "name": "Mandible",
        "data_type": "geometry.mesh",
        "semantic": "anatomy.bone.mandible",
        "features": [],
        "metadata": {}
    }

E o recurso pesado:

    resources/
        meshes/
            uuid.stl

ou outro formato interno/cache.