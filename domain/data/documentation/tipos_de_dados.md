Alguns tipos de dados vão ter atribuições e características específicas. Por exemplo uma malha de uma mandíbula em STL. É só uma malha, as ferramentas da pasta geometry vão gerir esta malha. 

Porém se eu definir no gestor de objetos que aquela malha é uma mandíbula os comportamentos e novas funcionalidades podem ser atribuídas à ela. Outro exemplo. Carreguei uma radiografia panorâmica, uma imagem 2D. Se eu clica nela as propriedades e ferramentas de edição devem ser condisentes com uma radiografia (Posso copiar/colar, posso enviar para um editor de imagens 2D etc... Porem não faz sentido submeter a operações booleanas 3D. ) Assim sucessivamente. 

Estrutura Proposta para o Sistema de Dados do OpenCMF
 
## 1. 📁 Volume (Dados Volumétricos / Imagens Médicas 3D)
Formatos principais: 
* .dcm (DICOM), 
* .vti, 
* .nrrd,
* .nii 

### Características
Contêm matrizes de voxels com intensidades (valores Hounsfield em CT, por exemplo).

### Comportamentos e Ferramentas:
  * Suportam renderização volumétrica (Volume Rendering - MPR: Coronal, Sagital, Axial).
  * Ferramentas de limiarização (Thresholding), segmentação e operações de processamento de imagem volumétrica. 
  * Não aceitam operações diretas de malha poligonal (como cortes de malha), exigindo conversão prévia (Marching Cubes) para gerar superfícies.
 
## 2. 🔺 Malha / Mesh (Geometrias 3D Poligonais)

Formatos principais: .stl, .ply, .obj, .vtk

* Subtipos anatômicos e protéticos:
* Anatômicos: Crânio, Maxila, Mandíbula, Dentes, Face, Olhos, Escaneamentos (Face/Intraoral).
* Dispositivos/Implantes: Implantes dentários, Pins, Implantes faciais, Placas de osteossíntese, Parafusos, Guias cirúrgicas.
* Segmentos: Corpo da mandíbula, Ramo direito, Ramo esquerdo, Mento (essenciais para ortognática).

### Características: 
Compostas por vértices, arestas e faces (trilhas poligonais).
Comportamentos e Ferramentas:Geridas pelas ferramentas da pasta geometry.Suportam operações booleanas, cortes, medições de volume/superfície e simulações de osteotomia.
Quando rotuladas semanticamente (ex: "Mandíbula"), habilitam fluxos específicos (ex: encaixe automático de placas, geração de guias de corte baseadas em landmarks).

## 3. 🖼️ Imagens 2DSubtipos:
* Referências (imagens de planejamento ou desenhos de face)Fotografias clínicas (perfil, frontal, sorriso)Pasta com fotografias (para pipelines de fotogrametria e reconstrução 3D)
* Radiografias (Panorâmica, Periapical, Telerradiografia lateral/frontal, PA de crânio) 

### Características
Arquivos matriciais 2D (.jpg, .png, .tiff, .dcm 2D).Comportamentos e Ferramentas:Ferramentas de edição 2D básicas (brilho, contraste, zoom, rotação, espelhamento, copiar/colar).Envio para editores externos ou painéis de comparação fotográfica pré/pós-operatória.## 

### Restrição
Bloqueadas para ferramentas 3D espaciais (como rotação tridimensional de malha ou cortes volumétricos).

4. 📈 Linhas e Curvas

* Subtipos: Splines, Curvas de Bézier, Linhas retas.

### Características
Entidades vetoriais 3D compostas por pontos de controle.Comportamentos e Ferramentas:Úteis para marcação de trajetos de nervos (ex: canal do nervo alveolar inferior), planejamento de osteotomias (linhas de corte no osso) ou eixos de simetria.📍 Marcações (Landmarks / Pontos Cefalométricos)Características: Coordenadas 3D pontuais $(x, y, z)$ no espaço anatômico.
### Comportamentos e Ferramentas
Base para análise cefalométrica 2D/3D.Servem como âncoras para alinhamento automático de modelos (registration / ICP), posicionamento de cefalostatos virtuais e cálculos de proporção.

## 5🧊 ROI / Deformers (Regiões de Interesse e Objetos de Deformação)

### Características: 
Primitivas geométricas simples (caixas, esferas, cilindros) ou volumes de influência.

### Comportamentos e Ferramentas
Utilizados para delimitar áreas de interesse para cálculo, máscara de dados ou aplicação de deformações locais (ex: simulação de ganho ou perda de tecido mole/duro baseada em retッジ/lattice deformation).📏 MediçõesSubtipos: Linhas angulares, Distâncias lineares (horizontais, verticais, profundidade).Características: Objetos derivados de pontos ou malhas que exibem valores métricos dinâmicos (milímetros ou graus).

### Comportamentos e Ferramentas
Atualização automática caso a geometria associada sofra alteração (ex: mover o mento atualiza a distância cefalométrica automaticamente).📐 Orientações e Referências AntropométricasSubtipos: Terços da face, Quintos da face, Proporções estéticas (Proporção Áurea).Características: Planos de referência (ex: Plano de Frankfurt, Plano de Camper) e grades de proporção facial.Comportamentos e Ferramentas:Auxiliam no diagnóstico estético e no posicionamento espacial correto do paciente no ambiente virtual.
 
## 6. 📝 Anotações em TextoCaracterísticas:
Notas descritivas livres ou associadas a pontos específicos da cena cirúrgica.
### Comportamentos e Ferramentas
Utilizadas para laudos rápidos, marcações de pontos de atenção para a equipe cirúrgica ou lembretes no plano de tratamento.
 
## 7. 🦴 Simulação CirúrgicaSubtipos: 
Módulos de ossos reposicionados (Bones - ex: frascos de blocos osteotomizados).
### Características
Contêm o estado lógico do planejamento (posição inicial vs. posição planejada / discrepância).Comportamentos e Ferramentas:Permitem calcular movimentos em translação ($X, Y, Z$) e rotação (Pitch, Roll, Yaw) para cirurgia ortognática.
 
## 8. 🧬 Regiões Anatômicas (Segmentações Semânticas de Malhas)

### Subtipos: 
Fronte, Nariz, Zigoma, Mento, Orelha, Lábio superior/inferior, Terços da face, Dentes, Língua, Mucosa, Vias aéreas.
### Características
Sub-malhas ou grupos de faces rotulados dentro de uma malha maior (ex: malha facial completa com regiões mapeadas).
### Comportamentos e Ferramentas
Comportamentos de deformação específicos (ex: simulação de tecidos moles puxados pelo deslocamento ósseo subjacente — Mass-spring systems ou Finite Element Analysis simplificado para tecidos moles).Análise volumétrica isolada (ex: cálculo do volume das vias aéreas para planejamento de apneia do sono - SAOS).


## Lista resumida: 
* Volume
	* Dicom
	* VTI
* Malha (Mesh)
	* Cranio
	* Maxila
	* Mandíbula
	* Dentes
	* Face
	* Olhos
	* Escaneamentos
	* Implantes dentários
	* Pins (Implantes dentários)
	* Implantes faciais
	* Placas (Osteossíntese)
	* Parafusos  (Osteossíntese)
	* Guias cirúrgicas
	* Segmentos (Ex: Corpo  mand + Ramos D e Ramo Esq + Mento)
* Imagens 
	* Referências; 
	* Fotografias;
	* Pasta com fotografias (Uma pasta que poderá ser utilizada para fotogrametria)  
	* Radiografias (Panorâmica; Periapical; Telerradiografia; PA), 
* Linhas
	* Splines
	* Bezier
	* Linhas retas; 
* Marcações (Que serão pontos, Landmark de cefalometria); 
* ROI/Deformers (Objetos 3D simples) 
* Medições
	* Linhas angulares
	* Distancias horizontais
* Orientações
	* Terços da face
	* Quintos da face
	* Proporções [Como proporção áurea])
* Anotações em texto
* Simulação cirúrgica
	* Bones
* Regiões anatômicas (Segmentações específicas de malhas com comportamento e deformação espessífica)
	* Fronte
	* Nariz
	* Zigoma
	* Mento
	* Orelha
	* Lábio sup, Lábio inf.
	* Terços sup, méd, Inf da face
	* Dentes
	* Língua
	* Mucosa
	* Vias aéreas

Estes objetos deverão ser organizados por hierarquia. Assim como acontece no cinema 4d. Exemplo. Uma mandíbula move sozinho. Porém um mento na hierarquia de um corpo mandibular será movimentado juntos. Se for aplicado um cor no corpo mandibular o mento também vai mudar de cor. Vão ser escalados juntos. Exemplo:
Mandíbula
	| Ramo Dir
	| Ramo Esq
	| Corpo mandibular
		| Dentes inf
		| Mento

