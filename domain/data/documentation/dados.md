A ideia fundamental

Você está propondo, na prática, três níveis:

* Geometria física

    “Tenho uma superfície triangular com vértices, faces e normais.”

* Tipo/semântica

    “Essa superfície representa uma mandíbula.”

* Capacidades comportamentais

    “Como é uma mandíbula, posso submetê-la a osteotomia, segmentação mandibular, movimentação ortognática, posicionamento de placa etc.”

## 1. Geometria Física (Mesh / PolyData)
### O que é: 
O dado bruto, independente de ser uma mandíbula, uma xícara ou um vaso cerâmico. São pontos no espaço $(x, y, z)$, topologia de conexões (faces/arestas) e vetores normais.
### Quem gere
A camada de computação gráfica e processamento de malhas (geometry).

### 2. Responsabilidade
Renderização rápida na tela, operações de cálculo espacial pura (interseções, booleanas brutas, suavização, decimação, cálculo de volume volumétrico ou de superfície).

## 2. Tipo / Semântica (Semantic Tag / Metadata)
### O que é
O rótulo ou identidade clínica do objeto. O sistema deixa de ver "um arquivo .stl genérico" e passa a saber que Object_01.stl = Mandíbula (ou Maxila, ou Nervo Alveolar, ou Placa de Osteossíntese).

### Responsabilidade
#### O Object Manager. 
É o dicionário que diz: "Este objeto pertence à categoria X e ao subtipo Y". Isso é fundamental para a árvore de projeto, salvamento de cenas em formato estruturado (JSON/XML) e exibição de ícones corretos na interface.
4. 
## 3. Capacidades Comportamentais (Behaviors / Actions / Rules)

O que é: O comportamento dinâmico e as regras de negócio associadas àquele tipo semântico. É o polimorfismo aplicado à cirurgia virtual.
### Responsabilidade
A camada de ferramentas clínicas e lógica de planejamento.Se o objeto é uma Mandíbula, o clique direito ou o menu de contexto libera: 

Criar plano de corte sagital no ramo, separar côndilo, realizar osteotomia sagital bilateral (BSSO), encaixar placa do sistema 2.0.

Se o objeto é uma Radiografia Panorâmica, ele herda comportamentos de 2D (brilho/contraste, zoom, régua de calibração) e bloqueia automaticamente qualquer tentativa de ferramenta 3D espacial.
Se o objeto é um Parafuso, ele ganha o comportamento de Snap-to-surface (encaixar magneticamente na malha óssea ou na placa).


                            OpenCMF Object
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                 Data Type                 Semantic Type
                     │                         │
               ┌─────┼─────┐            ┌──────┼──────┐
               │     │     │            │      │      │
             Mesh Volume Image       Mandible Tooth Implant
               │     │     │
               └─────┴─────┘
                     │
                Capabilities
                     │
             ┌───────┼────────┐
             │       │        │
           Boolean Measure Transform
                             │
                     Domain Behaviors
                             │
                  ┌──────────┼──────────┐
                  │          │          │
               Osteotomy  Orthognathic  Implant

## Exemplos:
### Mandible
    
    data_type:
        Mesh
    
    semantic_type:
        Anatomy.Bone.Mandible
    
    components:
        Transform
        Renderable
        Anatomical
        LandmarkContainer
        SurgicalObject
    
    capabilities:
        Boolean
        Measure
        Cut
        Transform
        Osteotomy
        Segmentation

### Panoramic_001

    data_type:
        Image2D
    
    semantic_type:
        Radiography.Panoramic
    
    components:
        Transform2D
        ImageProperties
        Renderable2D
    
    capabilities:
        Crop
        BrightnessContrast
        Rotate2D
        Copy
        Export
        ExternalEditor

## Fluxo
    Import DICOM
       ↓
    Volume
       ↓
    Segmentation
       ↓
    Surface extraction
       ↓
    Mesh
       ↓
    Semantic assignment
       ↓
    Mandible

## Capability Registry
Evitar colocar
    if object.type == "Mandible":
        show_osteotomy_tool()

Opção correta: 
    Mandible
        capabilities:
            Transform
            Measure
            Osteotomy
            Landmark
            Symmetry

    PanoramicRadiograph
        capabilities:
            Transform2D
            WindowLevel
            Crop
            Annotation
            Export
            ExternalEditor

## Estrutura:
| Componente           | Pergunta que responde                                              |
| -------------------- | ------------------------------------------------------------------ |
| `ObjectRegistry`     | **Quais objetos existem?**                                         |
| `ObjectFactory`      | **Como crio um objeto?**                                           |
| `ObjectTypeRegistry` | **Que tipos de objetos existem?**                                  |
| `SemanticRegistry`   | **O que esse objeto representa?**                                  |
| `CapabilityRegistry` | **O que esse objeto pode fazer?**                                  |
| `SceneGraph`         | **Onde esse objeto está e quem é seu pai/filho?**                  |
| `RelationshipGraph`  | **De quais outros objetos ele depende ou com quais se relaciona?** |
| `ComponentRegistry`  | **Quais componentes adicionais esse objeto possui?**               |


## Modelo de definição de dados:

    Object
    │
    ├── id
    ├── name
    ├── data_type
    │     └── geometry.mesh
    │
    ├── semantic_type
    │     └── anatomy.bone.mandible
    │
    ├── components
    │     ├── MeshComponent
    │     ├── TransformComponent
    │     └── RenderComponent
    │
    └── capabilities
          ├── Transform
          ├── Measure
          ├── Boolean
          ├── Cut
          ├── Osteotomy
          └── Landmark

    BaseObject
        │
        ├── datatype = Mesh
        ├── semantic = Mandible
        ├── features = [...]
        ├── capabilities = [...]
        └── relationships = [...]

sem precisar criar uma árvore monstruosa de classes:

* MandibleMesh
* MandibleSurgicalMesh
* MandibleOrthognathicMesh
* MandibleSegmentedMesh
* MandibleOsteotomyMesh


## Arquitetura

                    OBJECT
                      │
        ┌─────────────┼─────────────┐
        │             │             │
     DataType      Semantic      Features
        │             │             │
      Mesh       Mandible       Transform
     Volume      Maxilla        Render
    Image2D      Plate           Surgical
      Curve      Tooth
      Point
       ROI
                      │
                      ↓
                 Capabilities
                      │
             What can it do?

## Gerenciamento 

    ObjectSystem
    ├── Registry
    ├── Factory
    └── TypeRegistry


