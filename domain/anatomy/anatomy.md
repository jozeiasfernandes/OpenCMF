A pasta Anatomy é a camada de domínio clínico, cirúrgico e interativo do OpenCMF. Enquanto o núcleo Geometry opera de forma agnóstica apenas com matemática e computação gráfica pura, a pasta Anatomy consome essas geometrias e as veste com significado biológico, restrições biomecânicas e regras de planejamento cirúrgico.

É aqui que as estruturas anatômicas ganham identidade, relações espaciais específicas (como oclusão e articulação temporomandibular) e ferramentas de manipulação guiadas por lógica médica.

Descrição Detalhada dos Módulos

## 1. entities/ (Entidades Anatômicas)

Define as classes de alto nível que herdam ou encapsulam as malhas geométricas (Mesh):
* mandible.py: Representa a mandíbula. Possui propriedades para isolar regiões críticas ( ramo, corpo, côndilos e mento) e gerenciar estados de fragmentação pós-osteotomia.
* maxilla.py: Representa a maxila, contendo dados de alinhamento com a base do crânio e o plano oclusal maxilar.
* skull.py: A malha do crânio completo, servindo como referência estática e arcabouço visual para o caso.
* facial_scan.py: Gerencia a malha de tecidos moles da face, permitindo a fusão com os ossos e dentes para análise estética facial.
* dental_model.py: Trata das arcadas dentárias, essenciais para o encaixe oclusal e simulação da oclusão final do paciente.
* surgical_guide.py: Modela e prepara os dispositivos de transferência cirúrgica que serão fabricados por impressão 3D.


## 2. behaviors/ (Comportamentos e Lógica Clínica)

Contém a inteligência de domínio e as regras de interação biomecânica:orthognathic/: Gerencia a lógica de movimentação combinada (maxila + mandíbula), mantendo a integridade da relação oclusal durante o planejamento.tmj/: Modela o comportamento funcional das ATMs, avaliando o posicionamento dos côndilos na fossa mandibular antes e depois dos movimentos cirúrgicos.implant/: Regras para posicionamento tridimensional de implantes em relação a estruturas nobres (como o canal do nervo alveolar inferior).plastic_surgery/: Algoritmos de predição e ajuste de tecidos moles baseados no deslocamento das bases ósseas subjacentes.

## 3. gizmos/ (Gizmos Cirúrgicos e Espaciais)

Diferente de gizmos gráficos tradicionais (que apenas movimentam em $X, Y, Z$), estes widgets interativos possuem restrições anatômicas:mandibular_gizmo.py: Permite avanços, recuos e rotações da mandíbula respeitando os limites biomecânicos da oclusão e dos ramos.tmj_gizmo.py: Controla o eixo de rotação centrado especificamente na cabeça da mandíbula (côndilo).lefort_gizmo.py: Restringe o movimento da maxila aos vetores cirúrgicos clássicos de impacção, avanço, rebaixamento e rotação do plano oclusal.genioplasty_gizmo.py: Facilita o reposicionamento isolado do mento em direções sagitais, verticais e transversas.

4. landmarks/ (Marcos Anatômicos)

Módulo dedicado ao mapeamento de pontos cefalométricos tradicionais (como Násio, Cêntrico, Pogônio, Menton, A, B, entre outros) utilizados para diagnósticos e traçados cirúrgicos.

##5. measurements/ (Medições e Análises)

Ferramentas de mensuração clínica automatizada, capazes de calcular grandezas angulares e lineares da face, assimetrias esqueléticas e discrepâncias oclusais.

## 6. osteotomies/ (Linhas e Planos de Corte)

Contém os algoritmos e padrões geométricos que executam os cortes cirúrgicos virtuais programados no planejamento (como a Osteotomia Sagital Sutil do Ramo - BSSO, osteotomias Le Fort I e corticotomias).