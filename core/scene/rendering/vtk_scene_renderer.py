class VTKSceneRenderer:
    def __init__(self, renderer):
        self._renderer = renderer

    def add_actor(self, actor):
        """Apenas executa a adição ao motor gráfico."""
        self._renderer.AddActor(actor)

    def remove_actor(self, actor):
        """Apenas executa a remoção do motor gráfico."""
        self._renderer.RemoveActor(actor)

    def refresh(self):
        """Força a renderização da cena."""
        self._renderer.Render()
