Implementar as classes primitivas fundamentais para representação e armazenamento de dados espaciais 3D em memória, garantindo alta performance e uma API limpa para consumo por módulos de alto nível (como os algoritmos cirúrgicos na pasta Anatomy/).

## Tecnologias e Dependências Recomendadas
Antes de iniciar, é crucial definir a base de cálculo. Para alto desempenho em Python com computação gráfica:
* NumPy: Essencial para arrays de vértices, faces e operações matemáticas vetorizadas.
* Open3D / Trimesh / PyVista / VTK: (Opcional) Recomendo adotar uma dessas bibliotecas como motor interno para abstrair cálculos pesados, caso você não queira escrever a estrutura de dados C++ "do zero" em Python.  A classe Mesh pode simplesmente "envelopar" (encapsular) um trimesh.
Trimesh ou vtkPolyData.

## Fase 1: Fundação Espacial (Nuvem de Pontos e Base)

A estrutura mais simples em computação gráfica é um conjunto de pontos no espaço. Esta fase estabelece a fundação matemática usando arrays.Tarefas:Criar point_cloud.py:Definir a classe PointCloud.Atributos principais: vertices (array NumPy $N \times 3$).Métodos base: get_bounding_box(), get_center_of_mass(), apply_transform(matrix_4x4).

Testes (Fase 1):Gerar uma nuvem de pontos aleatória, aplicar translações/rotações e verificar se o centro de massa se desloca corretamente.Fase 2: Malhas de Superfície (O Núcleo)A malha poligonal é a estrutura mais utilizada no OpenCMF (arquivos STL/OBJ dos ossos e escaneamentos).

Tarefas:
## 1. Criar mesh.py:

Definir a classe Mesh (idealmente, herdando ou compondo comportamentos da PointCloud, já que toda malha possui vértices).Atributos principais: faces (array NumPy $M \times 3$ contendo os índices dos vértices para formar triângulos) e vertex_normals.Métodos base: compute_normals(), get_volume(), get_surface_area().

## 2. Topologia:
Implementar métodos de consulta topológica (ex: quais faces compartilham o vértice $X$?). Se usar bibliotecas como Trimesh, expor as propriedades de adjacência (edges_unique, face_adjacency).

Testes (Fase 2):Instanciar um cubo simples (8 vértices, 12 faces). Calcular normais, volume e área superficial e comparar com valores teóricos.

## 3. Fase 3: 

Estruturas Lineares (Curvas e Marcações)Curvas e polilinhas são fundamentais para marcação de caminhos de corte (osteotomias) ou desenho de guias cirúrgicos ao redor de dentes.

Tarefas:
### 1. Criar polyline.py:Definir a classe Polyline.

Atributos principais: 
Lista ordenada de pontos (vértices) conectados por segmentos de reta.Métodos base: get_length(), is_closed() (verifica se o primeiro e último ponto coincidem), e resample(distance) (redistribui pontos uniformemente ao longo da linha).

### 2. Criar curve.py:Definir a classe Curve (representação paramétrica).

Implementação: Pode utilizar Splines (B-splines ou Bezier) para curvas suaves. Ideal para marcar o trajeto do nervo alveolar inferior.

### 3. Testes (Fase 3):

Criar uma polilinha em ziguezague, calcular o comprimento total e testar a função de reamostragem (resampling) para garantir distâncias equidistantes.

## 4. Fase 4: 

O Domínio Volumétrico (Simulações)Necessário para a malha interna do osso e tecidos moles, fundamental se houver simulação de avanço de tecidos moles ou análise de elementos finitos (FEA).Tarefas:Criar volume_mesh.py:Definir a classe VolumeMesh.

Atributos principais: 
Em vez de faces 2D (triângulos), utilizar elementos 3D (tetraedros ou hexaedros). tetrahedra (array $K \times 4$).Métodos base: extract_surface() (extrai a malha externa, gerando um objeto da classe Mesh), get_total_volume().Testes (Fase 4):Gerar uma malha tetraédrica simples e extrair a superfície externa, verificando se ela produz um Mesh perfeitamente fechado (manifold).

## Próximos Passos Pós-Implementação

Assim que a fundação geometry/ estiver robusta e testada, as fases seguintes conectarão essa geometria com o resto do sistema:

Integração com io/: 
Criar os leitores e escritores de STL/OBJ para preencher a classe Mesh diretamente a partir de arquivos.Integração com algorithms/transforms/: Implementar as matrizes 4x4 para permitir que Mesh.apply_transform() funcione de maneira integrada.Encapsulamento na Anatomy/: Criar as instâncias de teste onde a classe Mandible instancia um Mesh com um arquivo STL real.