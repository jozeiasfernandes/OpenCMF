## 1. Visão Geral

A Home Page é o ponto de entrada da aplicação. Sua função é proporcionar uma interface intuitiva para o gerenciamento de pacientes e a escolha de fluxos clínicos. 

Ela atua como uma camada de apresentação de catálogo, operando estritamente sobre a camada de metadados e mantendo-se isolada da manipulação direta de arquivos ou diretórios.

## 2. Responsabilidades principais

* Visualização de Projetos: Exibir uma lista organizada de projetos existentes (pacientes) armazenados no sistema.

* Seleção e Criação: Permitir ao usuário selecionar um paciente existente para iniciar a sessão ou criar um novo registro.

* Seleção de Fluxo: Oferecer os fluxos de trabalho disponíveis para o paciente selecionado, servindo como guia para a inicialização da Workspace.

* Orquestração de UI: Capturar as intenções do usuário e emitir sinais de navegação para a MainWindow.

## 3. Integração com serviços

Para manter a Home_page leve e desacoplada, ela utiliza os seguintes serviços:

* ProjectService: O cérebro da vitrine. É consultado pela Home_page para:

* Listar projetos e metadados disponíveis na pasta patients/.

* Registrar novos pacientes ou fluxos (sem manipular a infraestrutura de pastas).

* Filtrar e organizar a visualização dos dados.

* FlowService: Focado na listagem e seleção das especialidades ou rotinas clínicas (flows/) que o usuário deseja aplicar ao paciente.

## 4. Fluxo de operação

* Carregamento: Ao abrir, a Home_page solicita ao ProjectService a lista de projetos e ao FlowService a lista de fluxos.

* Interação do Usuário:

* Ao selecionar um paciente, a Home_page dispara um sinal contendo o patient_path (caminho absoluto) e o fluxo escolhido.

* Entrega da Sessão: A MainWindow captura este sinal e entrega o contexto ao PatientManager, que assume a responsabilidade de ativar o paciente e carregar o patient_record.json.

## 5. Atribuições do Project_Service (da Home_Page)

Para manter o desacoplamento, estas são as funções estritas do serviço de catálogo:

* Catálogo de Projetos: Varre a pasta patients procurando por registros e metadados para popular a interface.

* Gestão de Metadados: Lê o arquivo patient_record.json (ou arquivos auxiliares) para obter nomes e datas, mas nunca altera a estrutura de arquivos da pasta do paciente.

* Registro de Projetos: Adiciona novos pacientes à lista da vitrine (interface) de forma rápida e segura.

* Exclusão da Vitrine: Remove a referência de um projeto da lista de exibição (a exclusão física do disco deve ser delegada ao Patient_Folder_Manager).