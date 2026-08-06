OpenCMF/
│
├── domain/                     # 🧠 Regras de Negócio Puras e Domínio Científico/Matemático
│   ├── anatomy/                # Estruturas anatômicas, landmarks e regiões
│   ├── geometry/               # Algoritmos geométricos, malhas e transformações espaciais
│   ├── simulation/             # Modelos físicos, predições e colisões
│   └── volume/                 # Processamento de imagens volumétricas (DICOM/Voxels)
│
├── application/                # ⚙️ Orquestração, Estado da Sessão e Casos de Uso
│   ├── commands/               # Padrão Command (Ações, Undo/Redo)
│   ├── patient/                # Gestão de dados do paciente ativo
│   ├── scene/                  # Estado e gerenciamento da cena 3D
│   ├── settings/               # Configurações do sistema e preferências
│   └── flows/                  # Fluxos de trabalho e wizards cirúrgicos
│
├── infrastructure/             # 💾 Persistência, E/S e Leitores Externos
│   └── imports/                # Leitores de arquivos externos (STL, DICOM, malhas)
│
├── ui/                         # 🖥️ Toda a interface gráfica e elementos visuais
│   ├── appearance/             # Ícones, temas e arquivos QSS
│   ├── color/                  # Gerenciamento de cores e seletores
│   ├── components/             # Bases, toolbars, sidepanels e tools visuais
│   ├── home_page/              # Tela inicial e editores de fluxo
│   └── workspace/              # Área de trabalho e gerenciadores de layout
│
├── modules/                    # 🧩 Módulos funcionais e extensões da aplicação
├── patients/                   # 📁 Diretório físico de dados e prontuários dos pacientes[cite: 1]
└── utils/                      # 🛠️ Funções utilitárias globais[cite: 1]