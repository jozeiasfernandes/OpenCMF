'''
SceneObject
   ↓
ActorFactory  (cria vtkActor)
   ↓
ActorRegistry (guarda referência)
   ↓
VTKSceneRenderer (aplica no VTK)
   ↓
VTK Engine



Gerencia:

renderer
add actor
remove actor
refresh


Ele só deve:

adicionar/remover vtkActor no renderer
atualizar a cena visual
forçar redraw (Render, Modified)
manter referência dos actors já criados

Ele NÃO deve saber:

o que é SceneObject
como criar um actor
regras de transformação
lógica de materiais

✔ Responsabilidade correta (precisa ser explícita)

O seu renderer deve:

✔ Fazer
AddActor
RemoveActor
Render / Refresh
SetVisibility / Opacity / Color (opcional)
❌ NÃO fazer
criar vtkActor
interpretar SceneObject
acessar registries
lógica de seleção
persistência

'''

class VTKSceneRenderer:
    def __init__(self, renderer):
        self._renderer = renderer
        self._actors = {}

    def add_actor(self, obj_id: str, actor):
        self._actors[obj_id] = actor
        self._renderer.AddActor(actor)

    def register_actor(self, obj_id: str, actor):
        """Regista um ator já adicionado ao renderer (evita AddActor duplicado)."""
        self._actors[obj_id] = actor

    def remove_actor(self, obj_id: str):
        actor = self._actors.pop(obj_id, None)
        if actor:
            self._renderer.RemoveActor(actor)

    def reset_tracked_actors(self):
        """Limpa o mapa local (p.ex. após remover atores diretamente do renderer)."""
        self._actors.clear()

    def refresh(self):
        self._renderer.Render()