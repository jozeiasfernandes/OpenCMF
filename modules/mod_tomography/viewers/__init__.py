# base_module.py (A casca)
# Contém apenas o comportamento visual comum: o QVTKRenderWindowInteractor,
# o indicator no canto (0,0) e o slider base_tool. É aqui que você colocará a lógica
# de maximizar/minimizar no futuro.
#
# planar.py (O especialista 2D)
# Herda de CentralAreaBase. Aqui você isola a lógica de MPR (Multi-Planar Reconstruction).
# Quando formos implementar o MIP (Maximum Intensity Projection), o código ficará restrito
# a este arquivo, sem poluir o resto.
#
# volume.py (O especialista 3D)
# Herda de CentralAreaBase. Aqui moram as funções de GPUVolumeRayCast, Threshold e,
# futuramente, os botões de Face de Orientação e Sombreamento.
#
# volume_viewer_widget.py (O Maestro)
# Este arquivo importa as classes acima. Ele não sabe como renderizar,
# ele apenas sabe onde colocar cada janela e como gerenciar o QComboBox de layout que você criou.


