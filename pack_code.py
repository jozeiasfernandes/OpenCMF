import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QTextEdit,
    QGroupBox, QFormLayout, QMessageBox, QProgressBar,
    QTreeWidget, QTreeWidgetItem, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon


class PackWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, root_dir, output_file, selected_dirs):
        super().__init__()
        self.root_dir = root_dir
        self.output_file = output_file
        self.selected_dirs = selected_dirs  # lista de caminhos absolutos selecionados

    def run(self):
        try:
            ignore_dirs = {'.git', '.venv', '__pycache__', '.idea', 'build', 'dist'}
            extensions = {'.py', '.ui'}

            self.progress.emit("Iniciando empacotamento seletivo...")

            with open(self.output_file, 'w', encoding='utf-8') as f:
                for root, dirs, files in os.walk(self.root_dir):
                    dirs[:] = [d for d in dirs if d not in ignore_dirs]

                    # Verifica se a pasta atual ou alguma pasta pai está selecionada
                    current_abs = os.path.abspath(root)
                    if not any(current_abs.startswith(sel) for sel in self.selected_dirs):
                        continue

                    for file in files:
                        if any(file.endswith(ext) for ext in extensions):
                            path = os.path.join(root, file)
                            rel_path = os.path.relpath(path, self.root_dir)

                            self.progress.emit(f"Adicionando: {rel_path}")

                            f.write(f"\n{'=' * 70}\n")
                            f.write(f"FILE: {rel_path}\n")
                            f.write(f"{'=' * 70}\n\n")

                            try:
                                with open(path, 'r', encoding='utf-8', errors='ignore') as code_file:
                                    f.write(code_file.read())
                                f.write("\n\n")
                            except Exception as e:
                                f.write(f"# Erro ao ler arquivo: {e}\n\n")

            self.finished.emit(True, f"✅ Projeto empacotado com sucesso!\nArquivo: {self.output_file}")
        except Exception as e:
            self.finished.emit(False, f"Erro: {str(e)}")


class PackProjectGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCMF - Pack Project")
        self.resize(1000, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Título
        title = QLabel("🗜️ OpenCMF - Pack Project")
        title.setStyleSheet("font-size: 26px; font-weight: bold; padding: 15px 0;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Splitter para dividir a tela
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # === ESQUERDA: Configurações + Lista de Pastas ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Configurações
        config_group = QGroupBox("⚙️ Configurações")
        config_layout = QFormLayout()

        self.root_edit = QLineEdit(".")
        btn_root = QPushButton("Selecionar Pasta Raiz")
        btn_root.clicked.connect(self.select_root_dir)

        root_hbox = QHBoxLayout()
        root_hbox.addWidget(self.root_edit)
        root_hbox.addWidget(btn_root)

        self.output_edit = QLineEdit("contexto.txt")
        btn_output = QPushButton("Salvar como...")
        btn_output.clicked.connect(self.select_output_file)

        output_hbox = QHBoxLayout()
        output_hbox.addWidget(self.output_edit)
        output_hbox.addWidget(btn_output)

        config_layout.addRow("Pasta Raiz:", root_hbox)
        config_layout.addRow("Arquivo de Saída:", output_hbox)
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)

        # Lista de Pastas (TreeView)
        folders_group = QGroupBox("📁 Lista de Pastas (selecione com checkbox)")
        folders_layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Pastas do Projeto")
        self.tree.setColumnCount(1)
        self.tree.itemChanged.connect(self.on_item_changed)
        folders_layout.addWidget(self.tree)

        btn_refresh = QPushButton("🔄 Atualizar Árvore")
        btn_refresh.clicked.connect(self.build_tree)
        folders_layout.addWidget(btn_refresh)

        folders_group.setLayout(folders_layout)
        left_layout.addWidget(folders_group)

        splitter.addWidget(left_widget)

        # === DIREITA: Log ===
        log_group = QGroupBox("📋 Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        splitter.addWidget(log_group)

        # Botão principal
        self.pack_btn = QPushButton("📦 EMPACOTAR PROJETO SELECIONADO")
        self.pack_btn.setStyleSheet("font-size: 17px; padding: 15px; font-weight: bold;")
        self.pack_btn.clicked.connect(self.start_packing)
        main_layout.addWidget(self.pack_btn)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.append_log("Interface carregada. Selecione a pasta raiz para começar.")

    def select_root_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Pasta Raiz", ".")
        if dir_path:
            self.root_edit.setText(dir_path)
            self.build_tree()

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar como", "contexto.txt", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.output_edit.setText(file_path)

    def build_tree(self):
        root_path = self.root_edit.text().strip()
        if not os.path.exists(root_path):
            QMessageBox.warning(self, "Erro", "Pasta raiz inválida!")
            return

        self.tree.clear()
        root_item = QTreeWidgetItem(self.tree, [os.path.basename(root_path) or root_path])
        root_item.setData(0, Qt.UserRole, root_path)
        root_item.setCheckState(0, Qt.Checked)
        self.add_subdirs(root_item, root_path)
        root_item.setExpanded(True)

    def add_subdirs(self, parent_item, parent_path):
        try:
            for item in sorted(os.listdir(parent_path)):
                full_path = os.path.join(parent_path, item)
                if os.path.isdir(full_path) and item not in {'.git', '.venv', '__pycache__', '.idea', 'build', 'dist'}:
                    child = QTreeWidgetItem(parent_item, [item])
                    child.setData(0, Qt.UserRole, full_path)
                    child.setCheckState(0, Qt.Checked)
                    self.add_subdirs(child, full_path)
        except:
            pass

    def on_item_changed(self, item, column):
        # Propagar estado do checkbox para filhos
        if item.childCount() > 0:
            state = item.checkState(0)
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, state)

    def get_selected_dirs(self):
        selected = []
        root = self.tree.topLevelItem(0)
        if not root:
            return [self.root_edit.text().strip()]

        def collect(item):
            if item.checkState(0) == Qt.Checked:
                path = item.data(0, Qt.UserRole)
                if path:
                    selected.append(os.path.abspath(path))
            for i in range(item.childCount()):
                collect(item.child(i))

        collect(root)
        return selected if selected else [self.root_edit.text().strip()]

    def append_log(self, message):
        self.log_text.append(message)

    def start_packing(self):
        root_dir = self.root_edit.text().strip()
        output_file = self.output_edit.text().strip()

        if not root_dir or not os.path.exists(root_dir):
            QMessageBox.warning(self, "Atenção", "Selecione uma pasta raiz válida.")
            return
        if not output_file:
            QMessageBox.warning(self, "Atenção", "Informe o arquivo de saída.")
            return

        selected_dirs = self.get_selected_dirs()

        self.pack_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.log_text.clear()
        self.append_log(f"Iniciando empacotamento de {len(selected_dirs)} pasta(s)...")

        self.worker = PackWorker(root_dir, output_file, selected_dirs)
        self.worker.progress.connect(self.append_log)
        self.worker.finished.connect(self.packing_finished)
        self.worker.start()

    def packing_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.pack_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "Sucesso", message)
            self.append_log("✅ Empacotamento concluído com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", message)

        self.append_log(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = PackProjectGUI()
    window.show()
    sys.exit(app.exec())