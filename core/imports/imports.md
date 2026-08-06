# Gestor de Imports

## 1. Objetivo

O **Gestor de Imports** é o componente central responsável por toda a entrada de dados no OpenCMF. Sua função é fornecer uma interface única e padronizada para importar exames, imagens, modelos tridimensionais e objetos auxiliares, independentemente do módulo clínico em utilização.

O Gestor de Imports elimina a necessidade de cada módulo implementar seu próprio mecanismo de importação, centralizando a seleção, validação, leitura e criação dos objetos que serão incorporados ao projeto e à cena.

Todo o processo de importação é executado localmente, preservando a privacidade dos dados do paciente e permitindo o funcionamento completo do OpenCMF sem dependência de conexão com a internet.

---

# 2. Objetivos Específicos

* Centralizar todas as importações do sistema.
* Padronizar o fluxo de importação para todos os módulos.
* Facilitar a inclusão de novos formatos de arquivo.
* Permitir reutilização do mesmo mecanismo em todo o OpenCMF.
* Fornecer uma interface intuitiva baseada no fluxo clínico.
* Exibir pré-visualização dos objetos antes da importação.
* Integrar automaticamente os objetos importados ao projeto e à Scene.

---

# 3. Estrutura da Interface

A interface será composta por três painéis principais.

+----------------------+----------------------+--------------------------------+
|                      |                      |                                |
| Frame 1              | Frame 2              | Frame 3                         |
| Categorias           | Origem               | Conteúdo                        |
|                      |                      |                                |
| Tomografias          | Projeto              | +----------------------------+ |
| Radiografias         | Arquivo              | |                            | |
| Escaneamentos        |                      | | File Browser / Galeria     | |
| Fotografias          |                      | |                            | |
| Malhas 3D            |                      | +----------------------------+ |
| Biblioteca           |                      |                                |
| Implantes Faciais    |                      | +----------------------------+ |
| Implantes Dentários  |                      | |                            | |
|                      |                      | | Preview                    | |
|                      |                      | |                            | |
|                      |                      | +----------------------------+ |
+----------------------+----------------------+--------------------------------+

## Painel 1 – Categorias

Responsável pela seleção do tipo de dado que será importado.

Categorias iniciais:

* Tomografias
* Radiografias
* Escaneamentos
* Fotografias
* Malhas 3D
* Biblioteca de Objetos
* Implantes Faciais
* Implantes Dentários

Cada categoria define quais formatos de arquivo e quais fontes de dados estarão disponíveis.

---

## Painel 2 – Origem

Após selecionar uma categoria, o usuário escolhe a origem dos dados.

Para a maioria das categorias:

* Projeto
* Arquivo

Para a Biblioteca de Objetos:

* Projeto
* Local
* Online

Essa separação permite que o mesmo mecanismo seja reutilizado em diferentes cenários sem alterar a interface.

A diferença é:

Projeto → galeria dos objetos/dados existentes no caso clínico.
Arquivo → abre o explorador de arquivos do sistema.
Biblioteca → galeria de objetos disponíveis para inserção.

---

## Painel 3 – Conteúdo

O terceiro painel será dividido em duas áreas utilizando um `QSplitter` vertical.



### Área Superior

Responsável pela navegação e seleção do conteúdo.

Seu comportamento depende da origem escolhida.

#### Projeto

Os arquivos pertencentes ao projeto serão apresentados em formato de **galeria**, utilizando miniaturas, nome e informações resumidas.

Exemplos:

* Tomografias do paciente.
* Malhas tridimensionais.
* Fotografias.
* Escaneamentos.

#### Arquivo

Será exibido um **OpenCMF File Browser**, substituindo o `QFileDialog` padrão do Qt.

Além da navegação convencional pelo sistema de arquivos, o navegador oferecerá:

* Locais favoritos.
* Locais recentes.
* Navegação rápida.
* Filtros automáticos conforme a categoria selecionada.
* Ícones específicos para cada tipo de arquivo.

#### Biblioteca

Os objetos serão apresentados como uma **biblioteca visual**, semelhante ao sistema de inserção de objetos do Meshmixer.

Exemplo:

* Crânio
* Maxila
* Mandíbula
* Esfera
* Cubo
* Marcadores

Cada item será apresentado por meio de um cartão contendo miniatura e nome.

---

### Área Inferior

Responsável pela pré-visualização do item atualmente selecionado.

Dependendo do tipo de objeto, poderão ser exibidos:

Tomografias

* Corte axial.
* Corte coronal.
* Corte sagital.
* Informações do volume.

Malhas 3D

* Renderização tridimensional.
* Número de vértices.
* Número de faces.
* Dimensões.

Fotografias

* Miniatura em alta resolução.

Objetos da Biblioteca

* Renderização 3D.
* Descrição.
* Categoria.

Implantes

* Modelo tridimensional.
* Fabricante.
* Código.
* Dimensões.

---

# 3. Categorias

## Tomografias

Formatos inicialmente suportados:

* DICOM
* VTI
* VTK
* NRRD
* NIfTI

---

## Radiografias

Categorias disponíveis:

* Panorâmica
* Telerradiografias
* Intrabucais

---

## Escaneamentos

Categorias:

* Face
* Arcadas

---

## Fotografias

Categorias:

* Extraorais
* Intraorais

---

## Malhas 3D

Importação de modelos tridimensionais.

O OpenCMF identificará automaticamente o formato do arquivo, sem exigir que o usuário escolha previamente a extensão.

---

## Biblioteca de Objetos

Catálogo de objetos reutilizáveis do OpenCMF.

Exemplos:

Biblioteca

├── Primitivas 3D
│   ├── Cubo
│   ├── Esfera
│   ├── Cilindro
│   └── Plano
│
├── Anatomia
│   ├── Crânio
│   ├── Maxila
│   ├── Mandíbula
│   ├── Zigoma
│   └── Órbita
│
├── Marcadores
│   ├── Ponto
│   ├── Plano
│   └── Eixos
│
└── Guias
    ├── Guia cirúrgico
    └── Templates

Esses objetos podem ser inseridos diretamente na cena, sem estarem vinculados aos dados clínicos do paciente.

---

## Implantes Faciais

Biblioteca destinada à inserção de implantes utilizados em cirurgia craniofacial.

---

## Implantes Dentários

Biblioteca destinada à inserção de implantes odontológicos.

---

# 5. OpenCMF File Browser

O OpenCMF utilizará um explorador de arquivos próprio, substituindo o `QFileDialog` convencional.

Principais funcionalidades:

* Navegação pelo sistema de arquivos.
* Locais favoritos.
* Locais recentes.
* Filtros automáticos por categoria.
* Pré-visualização integrada.
* Informações resumidas dos arquivos.

Esse navegador proporcionará uma experiência mais adequada para arquivos clínicos e modelos tridimensionais do que o seletor de arquivos padrão do sistema operacional.

OpenCMF File Browser

+------------------------------------------------+
| Localização                                    |
| C:\Paciente\Caso_001                           |
+------------------------------------------------+
| Arquivos                                       |
|                                                |
| [🖼] CT_Cranio                                 |
|     DICOM                                      |
|     512 x 512 x 380                            |
|                                                |
| [🖼] Mandibula.vti                             |
|     Volume VTK                                 |
|                                                |
+------------------------------------------------+
| Preview                                        |
|                                                |
|     imagem MPR / miniatura 3D                  |
|                                                |
+------------------------------------------------+
|          Cancelar       Importar               |
+------------------------------------------------+

---

# 6. Locais Favoritos

O usuário poderá registrar diretórios frequentemente utilizados.

Exemplos:

* Exames CBCT.
* Biblioteca de STL.
* Fotografias clínicas.
* Projetos de pesquisa.

Esses locais permanecerão disponíveis em futuras sessões do OpenCMF.

---

# 7. Biblioteca Online

A Biblioteca de Objetos poderá oferecer acesso opcional a um repositório online.

Esse recurso permitirá pesquisar e baixar novos objetos diretamente para a biblioteca local.

Após o download, os objetos permanecerão disponíveis offline.

O planejamento cirúrgico continuará sendo realizado integralmente de forma local.

---

# 8. Fluxo Geral

1. O usuário seleciona a categoria.
2. Escolhe a origem dos dados.
3. Navega pelo conteúdo disponível.
4. Visualiza uma prévia do item.
5. Confirma a importação.
6. O Gestor de Imports identifica automaticamente o importador adequado.
7. O objeto é validado e carregado.
8. O objeto é registrado no projeto.
9. O objeto é adicionado à Scene.
10. O Viewport é atualizado automaticamente.

---

# 9. Responsabilidades do Gestor de Imports

* Gerenciar a interface de importação.
* Selecionar automaticamente o importador apropriado.
* Validar arquivos antes da importação.
* Integrar objetos ao projeto.
* Atualizar a Scene.
* Gerenciar a biblioteca de objetos.
* Controlar favoritos e locais recentes.
* Exibir pré-visualizações.
* Permitir futura integração com bibliotecas online.

---

# 10. Responsabilidades com Scene

ImportManager
        │
        ▼
ImporterRegistry
        │
        ▼
BaseImporter
        │
        ├── validate()
        ├── load()
        └── create_object()
        │
        ▼
ImportManager
        │
        ├── salva no projeto
        ├── registra no histórico
        ├── adiciona à Scene
        └── atualiza o Viewport

Isso mantém o importador focado em uma única responsabilidade: converter uma fonte de dados (arquivo, pasta ou recurso) em um objeto do domínio do OpenCMF. Todo o restante da orquestração fica a cargo do ImportManager, o que torna a arquitetura mais limpa e facilita a manutenção.



---


# 11. Benefícios

A adoção de um Gestor de Imports centralizado proporciona:

* Interface consistente em todo o OpenCMF.
* Menor duplicação de código.
* Facilidade para adicionar novos formatos.
* Arquitetura modular.
* Melhor experiência de uso.
* Maior organização do sistema.
* Independência entre módulos clínicos.
* Base sólida para futuras expansões do software.
