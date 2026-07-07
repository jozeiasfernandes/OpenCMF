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
        # REMOVIDO: self._actors = {}

    def add_actor(self, actor):
        """Apenas executa a adição ao motor gráfico."""
        self._renderer.AddActor(actor)

    def remove_actor(self, actor):
        """Apenas executa a remoção do motor gráfico."""
        self._renderer.RemoveActor(actor)

    def refresh(self):
        """Força a renderização da cena."""
        self._renderer.Render()
