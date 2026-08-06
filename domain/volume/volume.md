## 1. Direção das Dependências
Camada 0 (Entrada):    dicom/
                         ↓
Camada 1 (Preparação): preprocessing/
                         ↓
Camada 2 (Processamento): segmentation/, processing/
                         ↓
Camada 3 (Análise):    analysis/
                         ↓
Camada 4 (Saída):      exporters/


## 2. Separação de Responsabilidades

Módulo          |	Responsabilidade                                |	Tipo de Operação
____________________________________________________________________________________________
dicom/          |	Leitura - Transforma arquivos DICOM em volume   |	I/O (entrada)
preprocessing/  |	Preparação - Melhora qualidade do volume        |	Transformação
segmentation/   |   Extração - Isola estruturas de interesse        |	Transformação
processing/     |  	Derivação - Gera novas representações           |	Transformação
analysis/       |	Interpretação - Extrai métricas e informações   |	Consulta
exporters/      |   Persistência - Salva resultados em disco        |	I/O (saída)

## 3. Fluxo de Dados
┌─────────────────────────────────────────────────────────────────┐
│                         FLUXO DE DADOS                          │
└─────────────────────────────────────────────────────────────────┘

[Arquivos DICOM]
    ↓
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA 0: ENTRADA                          │
│  dicom/ → Volume bruto (vtkImageData)                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA 1: PREPARAÇÃO                       │
│  preprocessing/ → Volume limpo, normalizado e reamostrado     │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│                 CAMADA 1.5: REGISTRO                        │
│  registration/ → Volume alinhado espacialmente              │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│            CAMADA 2: EXTRAÇÃO E DERIVAÇÃO                   │
│  segmentation/ → Máscaras (estruturas isoladas)             │
│  processing/   → Novas representações (MIP, Superfície)     │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│                CAMADA 3: INTERPRETAÇÃO                      │
│  analysis/ → Métricas, densidade, histogramas, forma        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│                   CAMADA 4: SAÍDA                           │
│  exporters/ → STL, OBJ, PLY, relatórios                     │
└─────────────────────────────────────────────────────────────┘

## 4. Comparação com Arquiteturas Conhecidas
* Clean Architecture: dicom/ atua como Gateway/Repository (fronteira de entrada de dados externos).

* Hexagonal Architecture: dicom/ mapeia a Porta de Entrada (Driver Port) e exporters/ mapeia a Porta de Saída (Driven Port).

* Pipeline Pattern: Sequência fluida preprocessing/ → registration/ → segmentation/ → processing/ → analysis/.

* Data Flow Architecture: Fluxo unidirecional de dados progressivamente transformados.

## 5. Ordem das Pastas por Nível de Abstração
Mais Concreto (Próximo a I/O / Hardware)
    ├── dicom/          ← Lida com arquivos brutos e decodificação
    ├── preprocessing/  ← Lida com voxels em memória
    ├── registration/   ← Lida com transformações espaciais
    ├── segmentation/   ← Lida com máscaras e topologia
    ├── processing/     ← Lida com representações geométricas
    ├── analysis/       ← Lida com interpretação clínica e métricas
    └── exporters/      ← Lida com persistência em disco
Mais Abstrato (Próximo ao Domínio / Negócio)

## 6. Visualização da Arquitetura
┌─────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO               │
│                    (ui/, viewers/)                      │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    CAMADA DE DOMÍNIO                    │
│  ┌───────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ analysis  │  │ processing  │  │   segmentation   │   │
│  └───────────┘  └─────────────┘  └──────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │                  registration/                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │                  preprocessing/                  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │                      dicom/                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    CAMADA DE INFRAESTRUTURA             │
│              (exporters/, utils/, reference/)           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 CORE/VOLUME (Processamento)                 │
├─────────────────────────────────────────────────────────────┤
│  models/         → Definição de dados estruturados          │
│  reference/      → Dados de referência e atlas anatômicos   │
│  dicom/          → [Camada 0] Entrada                       │
│  preprocessing/  → [Camada 1] Preparação                    │
│  registration/   → [Camada 1.5] Alinhamento                 │
│  segmentation/   → [Camada 2] Extração                      │
│  processing/     → [Camada 2] Derivação                     │
│  analysis/       → [Camada 3] Interpretação                 │
│  exporters/      → [Camada 4] Saída                         │
│  utils/          → Utilitários globais de voxels/arrays     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              VISUALIZATION (Apresentação Gráfica)           │
├─────────────────────────────────────────────────────────────┤
│  lut/            → Gerenciamento de cores e tabelas VTK     │
│  color_maps.py   → Paletas de cores complementares          │
│  annotations.py  → Anotações espaciais e overlays de tela   │
└─────────────────────────────────────────────────────────────┘