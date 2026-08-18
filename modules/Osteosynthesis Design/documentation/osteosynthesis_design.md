## 1. Descrição

O Osteosynthesis Design será um módulo paramétrico destinado à construção, edição e análise tridimensional de placas e parafusos de osteossíntese, inicialmente direcionado à traumatologia e à cirurgia ortognática. O módulo deverá permitir a criação de placas a partir de configurações predefinidas ou personalizadas, seguida da edição individual de seus elementos geométricos.

A unidade fundamental da placa será o PlateElement, que representa um segmento estrutural da placa e poderá apresentar ou não um furo. A presença do furo será tratada como uma propriedade do elemento, e não como uma entidade estrutural independente. Dessa forma, a transformação de um elemento perfurado em um segmento sem furo não modifica a topologia, as dimensões ou a quantidade de elementos da placa.

O sistema deverá permitir:

* construção paramétrica de placas;
* adição e remoção de elementos;
* criação e remoção de furos;
* alteração da angulação dos elementos e furos;
* curvatura e torção da placa;
* conexão entre elementos e entre placas;
* configuração de parafusos;
* adaptação à anatomia óssea;
* visualização tridimensional;
* preparação dos modelos para futuras análises por elementos finitos.

## 2. Objetivos funcionais

O módulo deverá contemplar:

1. Construção e edição tridimensional paramétrica de placas e parafusos de osteossíntese;
2. Adaptação e conformação das placas às superfícies ósseas;
3. Definição, posicionamento e análise da orientação dos parafusos;
4. Análise estrutural por elementos finitos (Finite Element Analysis – FEA);
5. Avaliação da distribuição de tensões, deformações e deslocamentos no sistema placa–parafuso–osso;
6. Identificação de regiões de concentração de tensões e avaliação de parâmetros mecânicos associados ao potencial de falha do sistema de osteossíntese.

## 3. Bibliotecas e tecnologias

A implementação será baseada em Python, mantendo a separação entre interface, modelo paramétrico, geometria e visualização.

Função	Tecnologia
Interface              	PySide6 / Qt
Modelagem geométrica	Open CASCADE Technology (OCCT)
Visualização             3D	VTK
Computação numérica 	NumPy
Algoritmos científicos	SciPy
Geração de malhas FEM	Gmsh — etapa futura
Solver FEA          	A definir — etapa futura
Persistência        	JSON


### Princípio arquitetural

    Plate Model
         │
         ▼
    Parametric Geometry
         │
         ▼
    OCCT
         │
         ├── B-Rep
         ├── Boolean
         ├── Extrusion
         ├── Chamfer
         ├── Transformation
         └── Surface operations
         │
         ▼
    Tessellation
         │
         ▼
    VTK
         │
         ▼
    3D Viewport

O OCCT será responsável pela geometria, enquanto o VTK será responsável pela visualização e interação tridimensional. A representação paramétrica permanecerá independente da malha utilizada para visualização.

## 4. Modelo conceitual

A placa será representada como uma sequência de elementos paramétricos:

    Plate
    │
    ├── Element 01
    ├── Element 02
    ├── Element 03
    ├── Element 04
    └── Element 05

Cada elemento possuirá propriedades próprias:

    PlateElement
    ├── geometry
    ├── length
    ├── width
    ├── thickness
    ├── orientation
    ├── deformation
    ├── hole
    └── connections[]

O furo será uma propriedade:

    hole = True

ou:

    hole = False

Assim:

    ●──●──────●──●

e

    ●──●──●──●

Podem possuir exatamente a mesma quantidade de PlateElement; apenas o estado dos furos foi alterado.

## 5. Plate Configuration Dialog

A ferramenta Create Plate iniciará a criação de uma nova placa e abrirá o diálogo Plate Configuration.

O diálogo será responsável pela definição das características iniciais da placa.

### 5.1 Presets

A configuração poderá ser carregada a partir de presets:

Preset
[ Reconstruction 2.4 mm ▼ ]


[ Load Preset ] [ Save Preset ]

Os presets poderão ser classificados como:

    Presets
    ├── System
    │   ├── Mini Plate
    │   ├── 2.0 System
    │   └── Reconstruction 2.4
    │
    └── User
        ├── Custom Plate 01
        └── Research Plate

Os presets do sistema serão protegidos contra alterações, enquanto o usuário poderá criar e salvar configurações personalizadas.

### 5.2 Plate

Parâmetros iniciais:

    Plate
    ├── Plate System
    ├── Thickness
    ├── Width
    └── Edge geometry

A espessura deverá ser selecionada por valores disponíveis no sistema:

Thickness
    [ 1.0 mm ▼ ]
    [ 1.5 mm ▼ ]
    [ 2.0 mm ▼ ]
    [ 2.4 mm ▼ ]

Os valores deverão posteriormente ser refinados a partir de levantamento de sistemas comerciais e literatura técnica.

### 5.3 Hole

    Hole
    ├── Hole Type
    ├── Diameter
    ├── Hole Pitch
    ├── Edge Distance
    └── Orientation
### Hole Type

O sistema deverá inicialmente contemplar:

    Non-locking
    Locking – Fixed Angle
    Locking – Variable Angle
    Combi
    Elongated Combi

O tipo de furo deverá controlar os parâmetros compatíveis com o sistema selecionado.

### Hole Pitch

A distância entre furos deverá ser definida pelo sistema de placa, evitando que o usuário altere arbitrariamente o espaçamento nominal entre furos.

    ●──────●──────●──────●
       pitch    pitch
#### Edge Distance

Define a distância mínima entre o furo e a borda da placa.

#### Hole Orientation

Define a orientação do eixo do furo em relação ao elemento.

## 6. Edge Geometry

A configuração inicial deverá contemplar:

    Edge
    ├── Edge Distance
    ├── Bevel Angle
    └── Edge Radius

O bisel poderá ser representado parametricamente:

            /
    ───────/
          ↑
        bevel

A geometria será reconstruída pelo OCCT após a alteração do parâmetro.

## 7. Screw Configuration

Os parafusos deverão ser associados a especificações compatíveis com o sistema de placa.

    Screw
    ├── Screw System
    ├── Diameter
    ├── Head Type
    ├── Head Diameter
    ├── Head Height
    └── Drive Type

Idealmente, a cabeça do parafuso não será desenhada manualmente. O usuário selecionará uma especificação do catálogo e o sistema gerará sua geometria correspondente.

## 8. Material

O material será definido independentemente das propriedades visuais:

    Material
    ├── Alloy
    ├── Density
    ├── Young's Modulus
    ├── Poisson's Ratio
    └── Mechanical Properties

A estrutura será preparada para utilização futura em análises por elementos finitos.

Exemplo:

    Material
    └── Ti-6Al-4V
        ├── Density
        ├── Young's Modulus
        └── Poisson's Ratio
## 9. Appearance

As propriedades visuais serão separadas das propriedades mecânicas:

    Appearance
    ├── Color
    ├── Metallic
    ├── Roughness
    └── Specular

A cor da placa deverá ser determinada pelo sistema de osteossíntese, permitindo identificação visual consistente entre placas compatíveis.

## 10. Ferramentas a serem construídas
### 10.1 Create Plate

Cria uma nova placa utilizando um Plate Configuration.

Create Plate
      ↓
Plate Configuration
      ↓
Create
      ↓
Plate Element 01

### 10.2 Select

Ferramenta geral de seleção.

Modos:

    Select
    ├── Plate
    ├── Element
    └── Connection

Também deverá permitir:

* seleção individual;
* seleção múltipla;
* box selection;
* brush selection;
* seleção sincronizada com a tabela.

### 10.3 Add Element

Adiciona um novo PlateElement.

    ●──●──●──●──[+]

O novo elemento será criado respeitando os parâmetros do sistema.

### 10.4 Delete Element

Remove um elemento selecionado.

A remoção não deverá necessariamente reorganizar os elementos restantes. A estrutura deverá permanecer consistente.

### 10.5 Add Hole / Remove Hole

Altera o atributo do elemento:

    hole = False
            ↓
    hole = True

ou:

    hole = True
            ↓
    hole = False

As dimensões do elemento permanecem inalteradas.

### 10.6 Add Multiple Elements

Ferramenta para criação rápida de vários elementos.

Duas modalidades são previstas:

Brush
    ●──●──●──●──●──●
          ╭────╮
          │ 🖌 │
          ╰────╯
Slider / Drag

O usuário desloca o cursor e o sistema apresenta uma prévia:

    Mouse position
          ↓
    ●──●──●──●──●──●
          6 elements

Ao clicar, a quantidade apresentada é confirmada.

### 10.7 Convert Hole / Solid

Permite transformar os elementos selecionados entre:

    Hole
      ↕
    Solid

Exemplo:

    ●──●──●──●──●──●

selecionar os elementos centrais:

    ●──●──[●──●──●]──●

e remover seus furos:

    ●──●──────────────●
    10.8 Angulation

Permite alterar a orientação relativa dos elementos ou dos furos.

    0°   →   5°   →   10°
    10.9 Bend

Aplica curvatura à placa.

Straight


    ●──●──●──●──●
    
    
            ↓
    
    
    Curved
    
    
      ╭────────╮
    ●            ●

### 10.10 Twist

Aplica torção à placa ou a um conjunto de elementos.

    E01 = 0°
    E02 = 2°
    E03 = 4°
    E04 = 6°
    E05 = 8°

### 10.11 Connect

Conecta elementos ou placas compatíveis.

Regra inicial:

Placas somente poderão ser conectadas quando apresentarem espessuras compatíveis.

Exemplo:

    Plate A 2.4 mm
          +
    Plate B 2.4 mm
          ↓
    Compatible

Enquanto:

    Plate A 1.0 mm
          +
    Plate B 2.4 mm
          ↓
    Incompatible

O sistema deverá impedir conexões incompatíveis.

## 11. Sistema de conectores

O sistema de conectores será responsável por representar relações geométricas entre elementos.

Um elemento poderá possuir múltiplas conexões:

       E03
      /   \
    E02   E04

Assim, um único furo poderá estar relacionado simultaneamente a dois elementos.

O modelo será representado como um grafo:

    Plate
    │
    ├── Element 01
    ├── Element 02
    ├── Element 03
    └── Element 04


    Connections
    ├── E01 ↔ E02
    ├── E02 ↔ E03
    └── E03 ↔ E04

Isso permitirá construir configurações como:

    Straight
    ●──●──●──●
    L
    ●──●
        │
        ●
        │
        ●

e:

    Y
        ●
        │
    ●───●───●

O sistema deverá validar a compatibilidade geométrica e estrutural das conexões.

## 12. Edição das placas

A edição será baseada em três níveis:

1. Plate Mode
2. Element Mode
3. Connection Mode

### Plate Mode

Atua sobre a placa inteira:

* espessura;
* largura;
* curvatura;
* torção;
* transformação;
* adaptação anatômica.
* Element Mode

Atua sobre elementos individuais:

* comprimento;
* orientação;
* posição;
* furo;
* angulação;
* deformação.

### Connection Mode

Atua sobre relações entre elementos:

* criação;
* remoção;
* posição;
* orientação;
* compatibilidade.

## 13. Interface de edição

A interface deverá combinar:

    ┌──────────────────────────────────────────────┐
    │ Toolbar                                      │
    ├──────────────┬───────────────────┬───────────┤
    │ Scene Tree   │                   │ Properties│
    │              │   3D Viewport     │           │
    │              │                   │           │
    │              │                   │           │
    ├──────────────┴───────────────────┴───────────┤
    │ Element Table / Parametric Editor            │
    └──────────────────────────────────────────────┘

A tabela permitirá representar a sequência de elementos:

    ┌────┬────┬────┬────┬────┬────┐
    │ E1 │ E2 │ E3 │ E4 │ E5 │ E6 │
    ├────┼────┼────┼────┼────┼────┤
    │ ●  │ ●  │    │    │ ●  │ ●  │
    └────┴────┴────┴────┴────┴────┘

A seleção na tabela deverá ser sincronizada com a seleção na viewport.

## 14. Fluxo de criação da placa

    Create Plate
          │
          ▼
    Plate Configuration
          │
          ├── Load Preset
          │
          ├── Plate System
          ├── Thickness
          ├── Width
          ├── Hole System
          ├── Hole Pitch
          ├── Edge Geometry
          ├── Screw System
          ├── Material
          └── Appearance
          │
          ▼
    Create
          │
          ▼
    Plate Element 01
          │
          ▼
    Add Element
          │
          ├── Element 02
          ├── Element 03
          └── ...
          │
          ▼
    Edit / Connect / Bend / Twist
          │
          ▼
    Final Plate


## 15. Fluxo de criação dos parafusos

Os parafusos deverão ser derivados da especificação selecionada para a placa.

    Plate System
          ↓
    Hole Specification
          ↓
    Compatible Screw System
          ↓
    Screw Specification
          ↓
    Generate Screw

O usuário poderá então:

* selecionar o furo;
* selecionar o parafuso compatível;
* posicionar o parafuso;
* modificar sua orientação dentro dos limites permitidos;
* visualizar a relação placa–parafuso–osso.

## 16. Construção dos sólidos

A geometria deverá ser construída de forma paramétrica.

Exemplo simplificado:

    PlateElement
          ↓
    2D Profile
          ↓
    Extrusion
          ↓
    Plate Solid
          ↓
    Hole Cylinder
          ↓
    Boolean Cut
          ↓
    Final Solid
    
    Para um elemento sem furo:
    
    2D Profile
          ↓
    Extrusion
          ↓
    Solid
    
    Para um elemento perfurado:
    
    2D Profile
          ↓
    Extrusion
          ↓
    Solid
          ↓
    Boolean Cut
          ↓
    Solid with Hole

O Open CASCADE Technology (OCCT) será utilizado como núcleo de modelagem geométrica.

## 17. Curvatura e torção

A geometria será reconstruída a partir dos parâmetros do modelo.

Por exemplo:

    Element 01 → Twist 0°
    Element 02 → Twist 2°
    Element 03 → Twist 4°
    Element 04 → Twist 6°

A alteração de um parâmetro não deverá exigir edição manual dos vértices da malha.

O fluxo será:

    Parameter
       ↓
    Parametric Model
       ↓
    Geometry Builder
       ↓
    OCCT
       ↓
    New Solid
       ↓
    Tessellation
       ↓
      VTK

## 18. Adaptação à superfície óssea

A placa poderá posteriormente ser adaptada à superfície óssea obtida de dados de imagem médica.

Fluxo previsto:

    Bone Surface
          +
    Initial Plate
          ↓
    Surface Analysis
          ↓
    Plate Adaptation
          ↓
    Parametric Deformation
          ↓
    Final Plate

A adaptação deverá preservar, tanto quanto possível, as restrições geométricas do sistema de placa e dos furos.

19. Construção e visualização dos sólidos

O modelo geométrico será mantido em uma representação independente da visualização.

    Parametric Model
          │
          ▼
    OCCT B-Rep
          │
          ▼
    Tessellation
          │
          ▼
    VTK PolyData
          │
          ▼
    GPU / Viewport

Isso permitirá que a malha visual seja atualizada sempre que um parâmetro for alterado.

O VTK será responsável por:

* renderização;
* iluminação;
* transparência;
* seleção;
* picking;
* câmera;
* clipping;
* interação tridimensional.

O OCCT permanecerá como fonte geométrica principal.

## 20. Validação geométrica

O módulo deverá possuir um mecanismo de validação antes da geração final do sólido.

Exemplos:

✓ Espessura válida
✓ Elemento com comprimento válido
✓ Furo dentro da placa
✓ Distância mínima da borda respeitada
✓ Hole Pitch válido
✓ Conexão compatível
✓ Geometria não degenerada

Situações inválidas:

✕ Furo fora da placa
✕ Furo sobreposto
✕ Elemento de comprimento zero
✕ Conexão incompatível
✕ Espessura incompatível
✕ Geometria autointersectante

O PlateValidator deverá impedir ou sinalizar a criação de geometrias inválidas.

## 21. Sistema de histórico

Todas as operações relevantes deverão ser implementadas como comandos reversíveis:

* Add Element
* Delete Element
* Add Hole
* Remove Hole
* Change Angle
* Connect
* Disconnect
* Bend
* Twist
* Merge
* Split
* Adapt

Fluxo:

    User Action
         ↓
    Command
         ↓
    Model Update
         ↓
    Geometry Rebuild
         ↓
    Viewport Update
    
    Isso permitirá:
    
    Undo
    Redo

sem necessidade de armazenar versões completas da malha tridimensional.

## 22. Persistência

A placa deverá ser armazenada como modelo paramétrico, e não apenas como STL.

Exemplo conceitual:

    {
        "type": "plate",
        "system": "reconstruction_2.4",
        "thickness": 2.4,
        "width": 8.0,
        "elements": [
            {
                "id": "E01",
                "hole": true,
                "orientation": 0
            },
            {
                "id": "E02",
                "hole": true,
                "orientation": 5
            },
            {
                "id": "E03",
                "hole": false,
                "orientation": 0
            }
        ]
    }

A geometria tridimensional poderá ser reconstruída a partir desses dados.

23. Arquitetura final resumida
                    OSTEosynthesis Design
                             │
              ┌──────────────┴──────────────┐
              │                             │
       Plate Configuration             Plate Editor
              │                             │
        Presets / Rules             Elements / Connections
              │                             │
              └──────────────┬──────────────┘
                             │
                      Parametric Model
                             │
                  ┌──────────┴──────────┐
                  │                     │
              PlateElement          Screw
                  │                     │
                  └──────────┬──────────┘
                             │
                       Geometry Builder
                             │
                           OCCT
                             │
                       B-Rep Solid
                             │
                        Tessellation
                             │
                           VTK
                             │
                       3D Viewport
                             │
                    ┌────────┴────────┐
                    │                 │
             Anatomical Model      FEA
                              (future)


## Princípio central

O módulo deverá representar placas e parafusos como objetos tridimensionais paramétricos, nos quais a geometria é consequência dos parâmetros e das relações entre elementos, e não uma malha estática editada diretamente.

Essa decisão é, na minha avaliação, a mais importante de toda a arquitetura. Ela permite que uma placa criada hoje possa ser posteriormente reconfigurada, adaptada à anatomia, conectada a outras placas, modificada e utilizada em uma análise biomecânica sem perder sua estrutura paramétrica original.