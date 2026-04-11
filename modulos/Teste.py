import json
import logging
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from core.base import ModuloBase


class Modulo(ModuloBase):
    def __init__(self):
        super().__init__()
        self.log_erros = []
        self._init_ui()

    def _init_ui(self):
        self.area_texto = QtWidgets.QTextEdit()
        self.area_texto.setReadOnly(True)
        # Estilo para parecer um terminal
        self.area_texto.setStyleSheet("background-color: #1b1e23; color: #2ecc71; font-family: 'Consolas';")

    def inicializar(self, caminho_paciente: str) -> None:
        """Executa a validação e espelha o resultado no Terminal."""
        super().inicializar(caminho_paciente)
        self.log_erros = []

        # --- LOG NO TERMINAL (PRINT) ---
        print("\n" + "=" * 50)
        print(f"DEBUG TERMINAL: Iniciando validação")
        print(f"CAMINHO RECEBIDO: {caminho_paciente}")
        print("=" * 50)

        if not caminho_paciente:
            msg = "ERRO: Caminho do paciente veio VAZIO para o módulo."
            print(f"[!] {msg}")
            self._adicionar_log(msg, "erro")
            return

        path_raiz = Path(caminho_paciente)

        # Validação da existência da pasta
        if not path_raiz.exists():
            msg = f"ERRO: A pasta física não existe: {path_raiz.absolute()}"
            print(f"[!] {msg}")
            self._adicionar_log(msg, "erro")
        else:
            print(f"[OK] Pasta raiz encontrada: {path_raiz.name}")
            self._adicionar_log(f"Pasta raiz verificada: {path_raiz.name}", "sucesso")

        # Validação do JSON
        path_json = path_raiz / "projeto" / "info.json"
        print(f"PROCURANDO JSON EM: {path_json.absolute()}")

        dados = self._validar_json_terminal(path_json)

        if dados:
            self._validar_pastas_terminal(path_raiz)
            print("[OK] Validação concluída com sucesso no terminal.")
            self._adicionar_log("JSON lido com sucesso. Veja os detalhes no terminal.", "sucesso")
            # Mostra o JSON formatado no terminal para inspeção rápida
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
        # Apenas para a interface visual
        cores = {"erro": "#e74c3c", "sucesso": "#2ecc71", "aviso": "#f1c40f"}
        cor = cores.get(tipo, "#ffffff")
        self.area_texto.append(f"<span style='color:{cor};'>{mensagem}</span>")

    def get_workspace(self) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.addWidget(QtWidgets.QLabel("<b>Verificação de Sistema (Check Terminal for details)</b>"))
        layout.addWidget(self.area_texto)
        return container