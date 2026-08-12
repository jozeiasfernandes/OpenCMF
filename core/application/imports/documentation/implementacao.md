# Plano de Implementação – Gestor de Imports

## Objetivo

Desenvolver um subsistema centralizado responsável por todas as importações do OpenCMF, permitindo a importação de exames, imagens, malhas tridimensionais, objetos da biblioteca e implantes por meio de uma interface única e padronizada.

O desenvolvimento será incremental, garantindo que cada etapa possa ser testada antes da implementação da próxima.

---

# Fase 1 – Estrutura do Subsistema

## Objetivo

Criar a estrutura inicial do pacote `core/imports`.

### Tarefas

* Criar a estrutura de diretórios.
* Implementar `ImportManager`.
* Implementar `ImporterRegistry`.
* Criar a classe `BaseImporter`.

### Resultado

Arquitetura básica pronta para receber novos importadores.

---

# Fase 2 – Interface do Gestor

## Objetivo

Construir a janela principal.

### Componentes

* ImportWindow
* CategoryPanel
* SourcePanel
* ContentPanel
* PreviewPanel

### Layout

```text
+--------------------------------------------------------------+
| Gestor de Imports                                            |
+--------------+--------------+--------------------------------+
| Categorias   | Origem       | Conteúdo                       |
|              |              |                                |
|              |              | -----------------------------  |
|              |              | Browser / Galeria             |
|              |              |                               |
|              |              |------------------------------- |
|              |              | Preview                       |
|              |              |                               |
+--------------+--------------+--------------------------------+
```

### Resultado

Interface funcional sem importação.

---

# Fase 3 – Painel de Categorias

Implementar:

* Tomografias
* Radiografias
* Escaneamentos
* Fotografias
* Malhas 3D
* Biblioteca
* Implantes Faciais
* Implantes Dentários

Ao selecionar uma categoria, o painel de origem deverá ser atualizado automaticamente.

---

# Fase 4 – Painel de Origem

Implementar:

Categorias clínicas

* Projeto
* Arquivo

Biblioteca

* Projeto
* Local
* Online

O painel de conteúdo deverá reagir dinamicamente à origem escolhida.

---

# Fase 5 – Browser/Galeria

Implementar o painel superior do terceiro frame.

## Projeto

Exibir os arquivos do projeto em formato de galeria.

Cada cartão deverá conter:

* miniatura;
* nome;
* tipo;
* informações resumidas.

---

## Arquivo

Implementar o OpenCMF File Browser.

Recursos:

* navegação;
* filtros;
* seleção;
* ordenação.

---

## Biblioteca

Exibir objetos como galeria visual.

Semelhante ao Meshmixer.

---

# Fase 6 – Painel de Preview

Implementar o painel inferior.

Tomografias

* corte axial;
* informações do volume.

Malhas

* renderização 3D.

Fotografias

* miniatura.

Biblioteca

* renderização.

---

# Fase 7 – Sistema de Favoritos

Implementar:

* adicionar favorito;
* remover favorito;
* editar nome;
* organizar favoritos.

---

# Fase 8 – Locais Recentes

Registrar automaticamente:

* últimos diretórios utilizados;
* últimos arquivos importados.

---

# Fase 9 – Scanner de Arquivos

Criar um serviço responsável por:

* localizar arquivos;
* filtrar extensões;
* identificar formatos;
* organizar resultados.

---

# Fase 10 – Sistema de Miniaturas

Criar geração automática de miniaturas.

Tomografias

* corte central.

Malhas

* renderização VTK.

Fotografias

* thumbnail.

Biblioteca

* imagem oficial.

---

# Fase 11 – Leitura de Metadados

Implementar leitura rápida.

DICOM

* modalidade;
* número de slices;
* voxel spacing.

Malhas

* vértices;
* faces;
* dimensões.

Fotografias

* resolução.

---

# Fase 12 – Registry de Importadores

Implementar o `ImporterRegistry`.

Responsabilidades:

* registrar importadores;
* localizar automaticamente o importador adequado;
* eliminar condicionais baseadas em extensão.

---

# Fase 13 – Importador de Malhas

Primeiro importador completo.

Responsabilidades:

* validar;
* carregar;
* criar objeto Mesh;
* registrar no projeto;
* adicionar à Scene.

---

# Fase 14 – Importador de Fotografias

Implementar:

* JPG
* PNG
* TIFF

---

# Fase 15 – Importador de Volumes

Implementar:

* VTI
* VTK
* NRRD
* NIfTI

---

# Fase 16 – Importador DICOM

Implementar:

* leitura de pasta DICOM;
* leitura de DICOMDIR;
* leitura de arquivo único;
* reconstrução do volume.

---

# Fase 17 – Importador de Escaneamentos

Implementar:

* Face
* Arcadas

---

# Fase 18 – Biblioteca de Objetos

Criar:

* LibraryManager;
* biblioteca local;
* categorias.

Objetos iniciais:

* Primitivas;
* Anatomia;
* Marcadores.

---

# Fase 19 – Biblioteca Online

Implementar:

* pesquisa;
* download;
* armazenamento local;
* atualização.

---

# Fase 20 – Implantes Faciais

Implementar:

* biblioteca local;
* inserção na cena.

---

# Fase 21 – Implantes Dentários

Implementar:

* biblioteca local;
* inserção na cena.

---

# Fase 22 – Integração com o Projeto

Após importar:

* copiar para o projeto (quando necessário);
* registrar metadados;
* atualizar índice de arquivos.

---

# Fase 23 – Integração com a Scene

Ao concluir a importação:

* criar objeto correspondente;
* adicionar à Scene;
* atualizar SceneTree;
* atualizar Viewport.

---

# Fase 24 – Seleção Múltipla

Permitir importar vários objetos simultaneamente.

Exemplo:

* várias fotografias;
* vários STL;
* vários exames.

---

# Fase 25 – Drag and Drop

Permitir:

* arrastar arquivos para o Viewport;
* arrastar para a Scene Tree;
* arrastar para o Workspace.

Todo o processo deverá reutilizar o `ImportManager`.

---

# Fase 26 – Histórico

Registrar:

* data;
* categoria;
* origem;
* arquivo;
* usuário (quando aplicável).

---

# Fase 27 – Testes

Testes unitários:

* Registry.
* Importadores.
* Browser.
* Favoritos.
* Miniaturas.

Testes de integração:

* Projeto.
* Scene.
* Workspace.

---

# Ordem Recomendada

1. Estrutura do subsistema.
2. Janela principal.
3. Painel de categorias.
4. Painel de origem.
5. Browser/Galeria.
6. Preview.
7. Favoritos.
8. Recentes.
9. Scanner de arquivos.
10. Miniaturas.
11. Metadados.
12. Registry.
13. Importador de Malhas 3D.
14. Importador de Fotografias.
15. Importadores de Volumes.
16. Importador DICOM.
17. Escaneamentos.
18. Biblioteca de Objetos.
19. Biblioteca Online.
20. Implantes Faciais.
21. Implantes Dentários.
22. Integração com o Projeto.
23. Integração com a Scene.
24. Seleção múltipla.
25. Drag and Drop.
26. Histórico.
27. Testes e documentação.

---

# Critérios de Conclusão

O Gestor de Imports será considerado concluído quando:

* Todas as categorias previstas estiverem operacionais.
* A interface responder dinamicamente às categorias e às origens selecionadas.
* O OpenCMF File Browser substituir o diálogo de arquivos padrão nas operações de importação.
* O sistema gerar miniaturas e pré-visualizações adequadas para cada tipo de dado.
* Os importadores forem registrados automaticamente pelo `ImporterRegistry`.
* Os objetos importados forem incorporados corretamente ao Projeto, à Scene e ao Viewport.
* A arquitetura permitir adicionar novos formatos e categorias sem modificar o núcleo do subsistema.
