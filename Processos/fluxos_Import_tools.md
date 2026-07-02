Para entender o fluxo de dados desde o clique do usuário até a visualização e manipulação 3D, imagine o sistema como uma esteira de montagem. Abaixo, apresento o resumo do fluxo arquitetural:

Resumo do Fluxo de Importação e Gestão de Cena
1. Ação do Usuário (ImportObjectTool):

    O usuário aciona a ferramenta. A ImportObjectTool abre um QFileDialog.
    
    Após a seleção, o arquivo é entregue ao ObjectManager.

2. Processamento e Persistência (ObjectManager):

    O ObjectManager valida o arquivo e o copia para a pasta do paciente (mantendo a integridade dos dados).
    
    Ele notifica o sistema de que um novo dado foi "fisicamente" importado.

3. Criação da Representação (SceneObject):

    Com os dados do arquivo, o sistema utiliza o SceneUtils para instanciar um SceneObject.
    
    Este objeto contém o ID único, o tipo (mesh, volume, etc.) e os dados brutos (VTK PolyData ou vti).
    
    Este objeto é registrado no SceneRegistry (ou gerenciador central de cena), tornando-se parte do "modelo" da aplicação.

4. Visualização (VTKActorFactory e Viewers):

    O SceneManager emite um evento (ex: OBJECT_ADDED).
    
    A VTKActorFactory escuta esse evento, recebe o SceneObject e cria o Ator VTK correspondente (a entidade gráfica que o VTK entende).
    
    Este ator é injetado nos vtkRenderers das Viewers, fazendo o objeto aparecer na tela.

5. Interação (BaseTool):

    Quando o usuário seleciona uma ferramenta (ex: de medição ou corte), a ferramenta recebe o InteractionContext.
    
    A ferramenta utiliza os pickers (via BaseTool) para identificar o ator na cena, mapeando-o de volta para o SceneObject original.
    
    Manipulações feitas pela ferramenta alteram o SceneObject, que por sua vez solicita a atualização do Ator na cena, fechando o ciclo.

Visualização do Fluxo de Responsabilidades:
Entrada: ImportObjectTool (Interação Humana)

Dados: ObjectManager (Persistência no Disco)

Modelo: SceneObject (Entidade Lógica dentro da Cena)

Visual: VTKActorFactory -> VTK Renderer (Representação Gráfica)

Controle: BaseTool (Manipulação lógica via InteractionContext)

Este fluxo garante que a lógica de "onde o arquivo está" (Disco) esteja isolada da lógica de "como ele é desenhado" (VTK), permitindo que você adicione novas ferramentas de manipulação sem precisar alterar a forma como os objetos são importados.