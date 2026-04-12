import json
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.base import ModuloBase


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.log_erros = []

        # --- CORREÇÃO: Criar o container e os widgets fixos no __init__ ---
        self.container_principal = QtWidgets.QWidget()
        self.area_texto = QtWidgets.QTextEdit()

        self._init_ui()

    def _init_ui(self):
        # Configuração da área de texto (Terminal Visual)
        self.area_texto.setReadOnly(True)
        self.area_texto.setStyleSheet(
            "background-color: #1b1e23; color: #2ecc71; font-family: 'Consolas';"
        )

        # --- CORREÇÃO: Montar o layout uma única vez aqui ---
        layout = QtWidgets.QVBoxLayout(self.container_principal)
        layout.addWidget(QtWidgets.QLabel("<b>Verificação de Sistema (Check Terminal for details)</b>"))
        layout.addWidget(self.area_texto)

    def inicializar(self, caminho_paciente: str) -> None:
        """Executa a validação e espelha o resultado na UI e no Terminal."""
        super().inicializar(caminho_paciente)

        # Limpa a interface para o novo paciente
        self.area_texto.clear()
        self.log_erros = []

        # --- LOG NO TERMINAL (PRINT) ---
        print("\n" + "=" * 50)
        print(f"DEBUG TERMINAL: Iniciando validação")
        print(f"CAMINHO RECEBIDO: {caminho_paciente}")
        print("=" * 50)

        if not caminho_paciente:
            msg = "ERRO: Caminho do paciente veio VAZIO."
            print(f"[!] {msg}")
            self._adicionar_log(msg, "erro")
            return

        path_raiz = Path(caminho_paciente)

        if not path_raiz.exists():
            msg = f"ERRO: Pasta física não encontrada: {path_raiz.absolute()}"
            print(f"[!] {msg}")
            self._adicionar_log(msg, "erro")
        else:
            print(f"[OK] Pasta raiz encontrada: {path_raiz.name}")
            self._adicionar_log(f"Pasta raiz verificada: {path_raiz.name}", "sucesso")

        path_json = path_raiz / "projeto" / "info.json"
        print(f"PROCURANDO JSON EM: {path_json.absolute()}")

        dados = self._validar_json_terminal(path_json)

        if dados:
            self._validar_pastas_terminal(path_raiz)
            print("[OK] Validação concluída com sucesso.")
            self._adicionar_log("JSON lido com sucesso. Verifique o terminal para detalhes.", "sucesso")
            print("\nCONTEÚDO DO JSON:")
            print(json.dumps(dados, indent=2, ensure_ascii=False))

        print("=" * 50 + "\n")

    def _validar_json_terminal(self, path: Path):
        if not path.exists():
            print(f"[!] ERRO: Arquivo info.json NÃO ENCONTRADO em: {path}")
            self._adicionar_log("info.json não encontrado.", "erro")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] ERRO AO LER JSON: {e}")
            self._adicionar_log(f"Falha na leitura do JSON: {e}", "erro")
            return None

    def _validar_pastas_terminal(self, raiz: Path):
        pastas = ["projeto", "modulo_tomografia", "modulo_osteotomia"]
        print("Checando subpastas...")
        for p in pastas:
            status = "OK" if (raiz / p).exists() else "AUSENTE"
            print(f"  -> Subpasta {p:20} : {status}")
            if status == "AUSENTE":
                self._adicionar_log(f"Pasta {p} faltando.", "aviso")

    def _adicionar_log(self, mensagem, tipo):
        """Adiciona mensagens à interface visual de terminal."""
        cores = {"erro": "#e74c3c", "sucesso": "#2ecc71", "aviso": "#f1c40f"}
        cor = cores.get(tipo, "#ffffff")
        # Como area_texto agora é persistente, o texto aparecerá na tela
        self.area_texto.append(f"<span style='color:{cor};'>{mensagem}</span>")

    def get_workspace(self) -> QtWidgets.QWidget:
        # --- CORREÇÃO: Retornar sempre a mesma referência fixa ---
        return self.container_principal