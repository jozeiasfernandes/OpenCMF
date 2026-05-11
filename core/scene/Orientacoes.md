Scene           -> Object	dados
ActorFactory    -> SceneObject → vtkActor
ActorRegistry   -> armazenamento
VTKSceneRenderer -> render pipeline
PropertySync -> atualização de estado visual


Fluxo de Funcionamento (Summary)
Ação: Usuário importa um STL.
Manager: scene_manager.add_object(obj).
Registry: Objeto é guardado no ObjectRegistry.
Bus: Evento OBJECT_ADDED é disparado.
Render Integration: Uma classe (ex: SceneBridge) escuta o evento, usa a VTKActorFactory para criar o vtkActor e o envia para o VTKSceneRenderer.