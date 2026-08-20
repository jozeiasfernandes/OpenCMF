A Régua é um Viewport Overlay, e não um objeto geométrico.

    Viewport
    ┌──────────────────────────────┐
    │  0  10  20  30  40 mm        │
    │                              │
    │                              │
    │            Scene             │
    │                              │
    │                              │
    │  0  10  20  30  40 mm        │
    └──────────────────────────────┘

A régua precisa conhecer a escala física.

No caso de CT:

    voxel spacing

determina a escala.

No caso de STL:

    mesh units

precisam estar corretamente definidas.

Portanto:

    Ruler
       ↓
    Viewport Scale
       ↓
    World Units

A régua utiliza o sistema global

                Core
                 │
            UnitSystem
                 │
                 ▼
             Viewport
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      Ruler     Grid   Measurement

A régua não precisa saber que o OpenCMF "escolheu mm". Ela pergunta:
    
    units.length_unit

e formata:

    0  10  20  30  40 mm


## Medições
Medir a distância entre dois pontos:
    Point A ───────────── Point B
                 24.73 mm


O cálculo deve ocorrer no espaço físico:

    distance = point_a.distance_to(point_b)

retornando:
    
    24.73

e a apresentação:

    units.format_length(distance)

produz:

    "24.73 mm"


## Volumes e Objetos

    CT
    │
    └── voxel spacing → mm
    
    IOS
    │
    └── mesh → mm
    
    Face Scan
    │
    └── mesh → mm
    
    STL
    │
    └── unidade interpretada → mm


Todos convergem para:

            OpenCMF
                 │
          Internal Units
                 │
                mm


## Quantities Framework

    └── Units
        ├── UnitSystem
        │
        ├── Length
        ├── Angle
        ├── Area
        ├── Volume
        ├── Mass
        └── Density


Inicialmente: 

    Length → mm
    Angle  → degrees

Futuramente:

    Area → mm²
    Volume → mm³
    Density → g/cm³


## Apresentação das unidades
O milimetro (mm) como unidade interna fixa, mas o usuário pode alterar a unidade de apresentação:

    Internal:
        mm
    
    Display:
        ┌──────────────┐
        │ Millimeter   │
        │ Centimeter   │
        │ Inch         │
        └──────────────┘

O Core trabalha em milímetros; a interface decide como os valores são exibidos.