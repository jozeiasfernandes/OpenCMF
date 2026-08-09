'''
Centraliza leitura/escrita de transformações sobre SceneObject.

- Normaliza formato position / rotation / scale (vectores de 3 floats).
- Operações relativas (translate, rotate em Euler°, scale por factor).
- Cópia entre objetos; snapshot/undo por id (pilha limitada).

ICP / alinhamento / landmarks podem usar este gestor como ponto único
para aplicar deltas e registar estado antes de alterações grandes.
'''

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from typing import Dict, List, Mapping, Sequence, Tuple, Optional

from application.scene import SceneObject

TransformDict = Dict[str, List[float]]

DEFAULT_POSITION: Tuple[float, float, float] = (0.0, 0.0, 0.0)
DEFAULT_ROTATION: Tuple[float, float, float] = (0.0, 0.0, 0.0)
DEFAULT_SCALE: Tuple[float, float, float] = (1.0, 1.0, 1.0)


def default_transform() -> TransformDict:
    return {
        "position": list(DEFAULT_POSITION),
        "rotation": list(DEFAULT_ROTATION),
        "scale": list(DEFAULT_SCALE),
    }


def _as_float_vec3(value: Sequence[float], fallback: Tuple[float, float, float]) -> List[float]:
    if value is None or len(value) < 3:
        return list(fallback)
    return [float(value[0]), float(value[1]), float(value[2])]


def normalize_transform(raw: Optional[Mapping[str, Sequence[float]]]) -> TransformDict:
    """Garante chaves position/rotation/scale com 3 componentes cada."""
    raw = raw or {}
    return {
        "position": _as_float_vec3(raw.get("position", DEFAULT_POSITION), DEFAULT_POSITION),
        "rotation": _as_float_vec3(raw.get("rotation", DEFAULT_ROTATION), DEFAULT_ROTATION),
        "scale": _as_float_vec3(raw.get("scale", DEFAULT_SCALE), DEFAULT_SCALE),
    }


class TransformManager:
    '''
    Gestor stateless relativamente aos SceneObjects; só muta os dicts nos objetos.
    Pilhas de undo são por ``object.id`` em memória.
    '''

    def __init__(self, max_undo_per_object: int = 64):
        self._max_undo = max(0, max_undo_per_object)
        self._undo_stacks: Dict[str, List[TransformDict]] = defaultdict(list)

    # ----- Leitura / escrita -----

    def get_transform_copy(self, obj: SceneObject) -> TransformDict:
        return normalize_transform(deepcopy(obj.transform))

    def replace_transform(self, obj: SceneObject, transform: Mapping[str, Sequence[float]]) -> None:
        obj.transform = normalize_transform(transform)

    def set_position(self, obj: SceneObject, x: float, y: float, z: float) -> None:
        obj.transform = normalize_transform(obj.transform)
        obj.transform["position"] = [float(x), float(y), float(z)]

    def set_rotation(self, obj: SceneObject, rx: float, ry: float, rz: float) -> None:
        obj.transform = normalize_transform(obj.transform)
        obj.transform["rotation"] = [float(rx), float(ry), float(rz)]

    def set_scale(self, obj: SceneObject, sx: float, sy: float, sz: float) -> None:
        obj.transform = normalize_transform(obj.transform)
        obj.transform["scale"] = [float(sx), float(sy), float(sz)]

    # ----- Operações relativas -----

    def translate(self, obj: SceneObject, dx: float, dy: float, dz: float) -> None:
        t = normalize_transform(obj.transform)
        p = t["position"]
        t["position"] = [p[0] + float(dx), p[1] + float(dy), p[2] + float(dz)]
        obj.transform = t

    def rotate_euler_deg(self, obj: SceneObject, drx: float, dry: float, drz: float) -> None:
        '''Soma deltas em graus (coerente com vtkActor.SetOrientation).'''
        t = normalize_transform(obj.transform)
        r = t["rotation"]
        t["rotation"] = [r[0] + float(drx), r[1] + float(dry), r[2] + float(drz)]
        obj.transform = t

    def scale_multiply(self, obj: SceneObject, sx: float, sy: float, sz: float) -> None:
        t = normalize_transform(obj.transform)
        s = t["scale"]
        t["scale"] = [s[0] * float(sx), s[1] * float(sy), s[2] * float(sz)]
        obj.transform = t

    def copy_transform_from(self, source: SceneObject, target: SceneObject) -> None:
        target.transform = normalize_transform(source.transform)

    # ----- Undo (snapshots por id) -----

    def push_undo(self, obj: SceneObject) -> None:
        if self._max_undo == 0:
            return
        stack = self._undo_stacks[obj.id]
        stack.append(normalize_transform(obj.transform))
        overflow = len(stack) - self._max_undo
        if overflow > 0:
            del stack[:overflow]

    def undo(self, obj: SceneObject) -> bool:
        stack = self._undo_stacks.get(obj.id)
        if not stack:
            return False
        snapshot = stack.pop()
        obj.transform = deepcopy(snapshot)
        return True

    def clear_undo(self, obj_id: str) -> None:
        self._undo_stacks.pop(obj_id, None)
