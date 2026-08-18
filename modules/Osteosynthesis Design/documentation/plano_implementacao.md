## Plano de implementação

Fase 1 — Modelo de domínio
* Plate
* PlateElement
* Hole
* Screw
* Connection
* Material
* PlatePreset

Fase 2 — Plate Configuration
* Create Plate
* Plate Configuration
* ComboBoxes;
* campos numéricos;
* presets;
* validação de parâmetros;
* preview 2D/3D.

Fase 3 — Motor geométrico
* integração OCCT;
* geração de sólidos;
* furos;
* chanfros;
* transformações;
* tesselação.

Fase 4 — Editor
* seleção;
* tabela de elementos;
* adição/remoção;
* Add Hole;
* angulação;
* conexão;
* bend;
* twist.

Fase 5 — Visualização
* integração VTK;
* picking;
* gizmos;
* seleção sincronizada;
* atualização em tempo real.

Fase 6 — Parafusos
* catálogo;
* especificações;
* geração geométrica;
* posicionamento;
* orientação;
* compatibilidade com furos.

Fase 7 — Adaptação anatômica
* importação da superfície óssea;
* posicionamento inicial;
* conformação;
* validação.

Fase 8 — Análise estrutural
* exportação geométrica;
* geração de malha;
* propriedades materiais;
* preparação do sistema placa–parafuso–osso;
* integração com FEA.