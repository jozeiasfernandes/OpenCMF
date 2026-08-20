## Orientação anatômica ≠ coordenadas da câmera


Camera

olhando para:

    Anterior
    Posterior
    Superior
    Inferior
    Left
    Right

Mas isso não significa necessariamente que o sistema de coordenadas mudou.


## OrientationSystem

com presets:

    FRONTAL
    POSTERIOR
    LEFT
    RIGHT
    SUPERIOR
    INFERIOR
    AXIAL
    SAGITTAL
    CORONAL

Cada preset configura a câmera.

Por exemplo:

    orientation.set_view("FRONTAL")
    orientation.set_view("SUPERIOR")
    orientation.set_view("INFERIOR")

Melhor do que cada módulo ter comandos próprios de câmera.