from PySide6 import QtWidgets


class SidePanelDrawerMixin:
    """
    Mixin responsável por isolar a lógica de comportamento de "gaveta"
    (recolhimento e expansão lateral com ajuste dinâmico do QSplitter).
    """

    def apply_drawer_state(self, collapsed: bool):
        """Oculta o conteúdo interno, ajusta a largura restrita e redimensiona o splitter pai."""
        if hasattr(self, "content_container"):
            self.content_container.setVisible(not collapsed)

        splitter = self._find_parent_splitter()

        if collapsed:
            # Fixa uma largura mínima/máxima restrita apenas para exibir a barra compacta
            self.setMaximumWidth(45)
            self.setMinimumWidth(35)
            if splitter:
                sizes = splitter.sizes()
                total = sum(sizes)
                if total > 0:
                    # Deixa quase todo o espaço para a área central e o mínimo para o painel lateral
                    splitter.setSizes([total - 40, 40])
        else:
            # Libera o painel para retornar ao tamanho normal gerido pelo usuário
            self.setMaximumWidth(16777215)  # QWIDGETSIZE_MAX
            self.setMinimumWidth(100)
            if splitter:
                sizes = splitter.sizes()
                total = sum(sizes)
                if total > 0:
                    # Restaura a proporção padrão de 70% para o centro e 30% para o painel
                    central_w = int(total * 0.70)
                    splitter.setSizes([central_w, total - central_w])

    def _find_parent_splitter(self) -> QtWidgets.QSplitter:
        """Busca recursivamente o QSplitter pai na hierarquia de widgets."""
        splitter = self.parent()
        while splitter and not isinstance(splitter, QtWidgets.QSplitter):
            splitter = splitter.parent()
        return splitter