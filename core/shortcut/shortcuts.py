"""
OpenCMF - Central de Atalhos e Comandos do Sistema
Este módulo centraliza todos os mapeamentos de teclado do aplicativo,
permitindo a separação de escopos (Global, 3D e 2D) e facilitando a futura
customização por parte do usuário.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence

# ==============================================================================
# REGISTRO MESTRE DE AÇÕES (Dicionário de Configuração)
# ==============================================================================
# O formato da chave 'contexto.acao' garante unicidade.
# O campo 'current' define o atalho ativo (pode ser uma String ou Qt.Key).

ACTIONS_REGISTRY = {
    # --- ESCOPO: GLOBAL (Application-Wide) ---
    "global.open": {
        "category": "Global",
        "description": "Abrir Arquivo/Projeto",
        "default": "Ctrl+O",
        "current": "Ctrl+O",
    },
    "global.save": {
        "category": "Global",
        "description": "Salvar Projeto",
        "default": "Ctrl+S",
        "current": "Ctrl+S",
    },
    "global.close_tab": {
        "category": "Global",
        "description": "Fechar Aba Atual",
        "default": "Ctrl+W",
        "current": "Ctrl+W",
    },
    "global.print": {
        "category": "Global",
        "description": "Imprimir",
        "default": "Ctrl+P",
        "current": "Ctrl+P",
    },
    "global.full": {
        "category": "Global",
        "description": "Alternar Tela Cheia",
        "default": Qt.Key_F11,
        "current": Qt.Key_F11,
    },
    "global.component_list": {
        "category": "Global",
        "description": "Exibir Lista de Componentes",
        "default": "Ctrl+L",
        "current": "Ctrl+L",
    },
    "global.home": {
        "category": "Global",
        "description": "Ir para a Home",
        "default": "Ctrl+H",
        "current": "Ctrl+H",
    },

    # --- ESCOPO: VISUALIZAÇÃO 3D (3D View) ---
    "view3d.frontal": {
        "category": "Câmera 3D",
        "description": "Visão Frontal",
        "default": Qt.Key_1,
        "current": Qt.Key_1,
    },
    "view3d.right": {
        "category": "Câmera 3D",
        "description": "Visão Direita",
        "default": Qt.Key_2,
        "current": Qt.Key_2,
    },
    "view3d.left": {
        "category": "Câmera 3D",
        "description": "Visão Esquerda",
        "default": Qt.Key_3,
        "current": Qt.Key_3,
    },
    "view3d.superior": {
        "category": "Câmera 3D",
        "description": "Visão Superior",
        "default": Qt.Key_4,
        "current": Qt.Key_4,
    },
    "view3d.inferior": {
        "category": "Câmera 3D",
        "description": "Visão Inferior",
        "default": Qt.Key_5,
        "current": Qt.Key_5,
    },
    "view3d.orthogonal": {
        "category": "Câmera 3D",
        "description": "Alternar para Câmera Ortogonal",
        "default": Qt.Key_O,
        "current": Qt.Key_O,
    },
    "view3d.mandible": {
        "category": "Anatomia 3D",
        "description": "Isolar/Focar Mandíbula",
        "default": Qt.Key_M,
        "current": Qt.Key_M,
    },
    "view3d.maxilla": {
        "category": "Anatomia 3D",
        "description": "Isolar/Focar Maxila",
        "default": Qt.Key_N,
        "current": Qt.Key_N,
    },
    "view3d.skull": {
        "category": "Anatomia 3D",
        "description": "Isolar/Focar Crânio",
        "default": Qt.Key_B,
        "current": Qt.Key_B,
    },
    "view3d.chin": {
        "category": "Anatomia 3D",
        "description": "Isolar/Focar Mento (Queixo)",
        "default": Qt.Key_V,
        "current": Qt.Key_V,
    },
    "view3d.translate": {
        "category": "Ferramentas 3D",
        "description": "Ativar Translação",
        "default": Qt.Key_T,
        "current": Qt.Key_T,
    },
    "view3d.scale": {
        "category": "Ferramentas 3D",
        "description": "Ativar Escala",
        "default": Qt.Key_E,
        "current": Qt.Key_E,
    },
    "view3d.rotate": {
        "category": "Ferramentas 3D",
        "description": "Ativar Rotação",
        "default": Qt.Key_R,
        "current": Qt.Key_R,
    },
    "view3d.pan": {
        "category": "Ferramentas 3D",
        "description": "Ativar Ferramenta Mover (Pan)",
        "default": Qt.Key_P,
        "current": Qt.Key_P,
    },
    "view3d.zoom": {
        "category": "Ferramentas 3D",
        "description": "Ativar Ferramenta Zoom",
        "default": Qt.Key_Z,
        "current": Qt.Key_Z,
    },
    "view3d.delete_object": {
        "category": "Ações 3D",
        "description": "Atualizar view",
        "default": Qt.Key_Space,
        "current": Qt.Key_Space,
    },
    "view3d.import_objects": {
        "category": "Ações 3D",
        "description": "Importar Objetos 3D",
        "default": "Ctrl+I",
        "current": "Ctrl+I",
    },
    "view3d.delete_object": {
        "category": "Ações 3D",
        "description": "Deletar Objeto Selecionado",
        "default": "Ctrl+Delete",
        "current": "Ctrl+Delete",
    },

    # --- ESCOPO: MULTIPLANAR 2D (MPR) ---
    "mpr.axial": {
        "category": "Orientações MPR",
        "description": "Mudar para Visão Axial",
        "default": Qt.Key_A,
        "current": Qt.Key_A,
    },
    "mpr.coronal": {
        "category": "Orientações MPR",
        "description": "Mudar para Visão Coronal",
        "default": Qt.Key_C,
        "current": Qt.Key_C,
    },
    "mpr.sagittal": {
        "category": "Orientações MPR",
        "description": "Mudar para Visão Sagital",
        "default": Qt.Key_S,
        "current": Qt.Key_S,
    },
    "mpr.3d": {
        "category": "Orientações MPR",
        "description": "Focar Visualização no Espaço 3D",
        "default": Qt.Key_D,
        "current": Qt.Key_D,
    },
    "mpr.ruler": {
        "category": "Ferramentas MPR",
        "description": "Ativar Régua de Medição",
        "default": "Ctrl+R",
        "current": "Ctrl+R",
    },
    "mpr.guides": {
        "category": "Ferramentas MPR",
        "description": "Alternar Linhas de Guia",
        "default": "Ctrl+G",
        "current": "Ctrl+G",
    },
}


# ==============================================================================
# FUNÇÕES DE INTERRUPÇÃO E CONSULTA (APIs para os Widgets)
# ==============================================================================

def get_shortcuts_by_scope(scope_prefix: str) -> dict:
    """
    Retorna um dicionário otimizado para o método `keyPressEvent` de um Widget.
    Une atalhos puros (Qt.Key) e sequências combinadas (Ctrl+Chave) convertidas.

    Exemplo de retorno para 'mpr':
    {
        Qt.Key_A: "mpr.axial",
        "Ctrl+R": "mpr.ruler"
    }
    """
    scope_shortcuts = {}

    for action_id, info in ACTIONS_REGISTRY.items():
        if action_id.startswith(f"{scope_prefix}."):
            shortcut = info["current"]
            scope_shortcuts[shortcut] = action_id

    return scope_shortcuts


def match_shortcut(event, shortcut_map: dict) -> str | None:
    """
    Gerenciador auxiliar para correspondência de teclas no PySide6.
    Avalia chaves normais e strings de modificadores como 'Ctrl+S'.

    Retorna o ID da ação correspondente ou None caso não encontre.
    """
    # 1. Tenta correspondência direta por tecla pura (Ex: Qt.Key_1)
    if event.key() in shortcut_map:
        return shortcut_map[event.key()]

    # 2. Se falhar, tenta converter o evento atual em String para bater com "Ctrl+X"
    key_sequence = QKeySequence(event.modifiers() | event.key())
    event_str = key_sequence.toString()

    if event_str in shortcut_map:
        return shortcut_map[event_str]

    return None