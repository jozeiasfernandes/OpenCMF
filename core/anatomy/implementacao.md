## Plano de Implementação: Módulo Anatomy
Este plano define a estratégia de desenvolvimento progressivo para a pasta Anatomy, partindo das fundações estruturais (entidades e regiões) até as lógicas mais complexas de comportamento, restrições e simulações cirúrgicas.

## Fase 1: Fundações e Entidades Anatômicas (entities/ e regions/)
O objetivo desta fase é criar os objetos que herdam/encapsulam o motor geométrico (Geometry) e injetam contexto biológico, além de isolar estruturas críticas.

### Tarefas:

* Criar entities/: Implementar as classes base e específicas (mandible.py, maxilla.py, skull.py, facial_scan.py, dental_model.py, surgical_guide.py) herdando de Mesh. Adicionar propriedades intrínsecas (ex: divisão da mandíbula em ramos e corpo).

* Criar regions/: Desenvolver os módulos para rastreamento e isolamento de estruturas nobres (inferior_alveolar_canal.py, condyle.py, maxillary_sinus.py).

* Critério de Sucesso: Instanciar uma malha STL genérica como um objeto Mandible e conseguir consultar seus subcomponentes anatômicos isolados.

## Fase 2: Referências e Oclusão (landmarks/, measurements/ e occlusion/)
Estabelecer o sistema de diagnóstico métrico e a relação dentária, essenciais para qualquer planejamento ortognático.

Tarefas:

* Criar landmarks/: Implementar o mapeamento de pontos cefalométricos (cephalometric.py) e marcações cirúrgicas personalizadas (custom_points.py).

* Criar measurements/: Desenvolver o cálculo de grandezas lineares, angulares, assimetrias faciais (metrics.py) e relatórios analíticos (analysis.py, reports.py).

* Criar occlusion/: Implementar a representação dos arcos dentários (arch.py), cálculo de pontos de contato oclusal (contacts.py) e a relação intermaxilar (intermaxillary.py).

* Critério de Sucesso: Marcar pontos de referência em uma arcada e calcular automaticamente a distância interdental e os contatos oclusais estáticos.

## Fase 3: Restrições Biomecânicas e Gizmos (constraints/ e gizmos/)
Implementar a inteligência de limites e a interface interativa restrita, garantindo que o cirurgião planeje dentro de parâmetros seguros.

### Tarefas:

* Criar constraints/: Desenvolver a classe base de restrições (base_constraint.py) e as regras específicas (occlusion_constraint.py, tmj_constraint.py, collision_constraint.py, bone_contact_constraint.py, dental_constraint.py, soft_tissue_constraint.py).

* Criar gizmos/: Implementar os widgets de manipulação espacial guiados por semântica cirúrgica (mandibular_gizmo.py, tmj_gizmo.py, lefort_gizmo.py, genioplasty_gizmo.py), integrando-os diretamente às constraints da fase anterior.

* Critério de Sucesso: Tentar mover a mandíbula usando o mandibular_gizmo e verificar se a restrição de oclusão ou colisão condilar bloqueia ou limita o movimento indevido.

## Fase 4: Osteotomias e Comportamentos Cirúrgicos (osteotomies/ e behaviors/)
Automatizar os cortes cirúrgicos virtuais e as simulações cinemáticas de movimentação bimaxilar e tecidual.

### Tarefas:

* riar osteotomies/: Implementar a classe base de cortes (base/osteotomy.py) e os padrões cirúrgicos clássicos: Maxila (lefort1.py, lefort2.py, lefort3.py), Mandíbula (bsso.py, ivro.py, vertical.py) e Mento (genioplasty.py).

* Criar behaviors/: Desenvolver as regras globais de movimentação ortognática (orthognathic.py), dinâmica da ATM (tmj.py), planejamento de implantes (implant.py) e predição estética (plastic_surgery.py).

* Critério de Sucesso: Executar virtualmente uma osteotomia BSSO na mandíbula, separar o segmento proximal do distal e reposicioná-lo respeitando as regras ortognáticas.

## Fase 5: Predição de Tecidos Moles (soft_tissue/)
Finalizar o ciclo de planejamento com a simulação do impacto estético facial externo gerado pelas alterações ósseas.

### Tarefas:

* Criar soft_tissue/: Implementar o mapeamento de espessura cutânea (thickness_map.py), algoritmos de deformação elástica da malha de tecidos moles (mesh_simulation.py) e predição de perfil (profile_prediction.py).

* Critério de Sucesso: Movimentar a maxila e a mandíbula (Fase 4) e observar a malha de facial_scan se deformar de maneira coerente e proporcional na região cutânea.