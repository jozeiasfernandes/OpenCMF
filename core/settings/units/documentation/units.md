## Unidade interna canônica

    Comprimento = milímetro (mm)

Isso significa que, internamente:

    1 unidade de comprimento = 1 mm

Assim:

    mandible.position.x = 35.2

significa:

    35.2 mm

Não precisaremos ficar convertendo unidades em cada módulo.


Não colocaremos "mm" nos objetos espalhado pelo código.. Evitaria:

    mandible.x = "35.2 mm"

e também:

    mandible.x = 35.2  # mm


O ideal é que o Core saiba que a unidade canônica é mm:

    mandible.transform.position.x = 35.2

O significado físico é determinado pelo UnitSystem.


## Unidades

1. UnitSystem
2. LengthUnit
3. AngleUnit


### Conceitualmente

    UnitSystem.length = "mm"
    UnitSystem.angle = "deg"

Mas internamente os valores poderiam permanecer normalizados.

Isso permite futuramente:

    mm
    cm
    m
    inch

sem alterar a geometria.

## Estrutura de pastas  
│   ├── Units
    │   │   ├── UnitSystem
    │   │   ├── Length
    │   │   ├── Angle
    │   │   ├── Area
    │   │   └── Volume


