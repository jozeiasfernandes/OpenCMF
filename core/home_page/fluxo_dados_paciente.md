O Fluxo de Dados Unificado passo a passo:

Início na Home_page: O usuário interage com os serviços de projeto e fluxo para selecionar um paciente existente ou criar um novo. A seleção emite o caminho do projeto (patient_path) em conjunto com a escolha de um fluxo de trabalho.

Coordenação no main (MainWindow): A janela principal intercepta os sinais vindos da página inicial, armazena o caminho em self.current_patient_path e inicializa o arquivo de configuração e as dependências do fluxo por meio do ProjectServiceHomePage e da WorkspaceManager.

Gerenciamento na Workspace e Mixins (WorkspaceManager e WorkspacePatientMixin): A área de trabalho centraliza o estado global da sessão do paciente utilizando o WorkspaceState (que emite sinais reativos de mudança) e o WorkspacePatientMixin (responsável por verificar e propagar o caminho de forma segura).

Destino no Módulo (Module Patient): Por fim, a workspace localiza o módulo ativo correspondente e dispara o método de inicialização (modulo.inicializar(caminho_paciente)), fazendo com que o ProjectServiceHomePage carregue o arquivo info.json e popule as respectivas abas de dados, arquivos e projetos do paciente.