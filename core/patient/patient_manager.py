from pathlib import Path
from typing import Optional, Dict, Any
from PySide6 import QtCore


class PatientManager(QtCore.QObject):
    """
    Gerenciador centralizado e reativo da sessão do paciente na aplicação (Singleton).
    Responsável por manter o estado global do paciente ativo e notificar a UI e os módulos.
    """

    _instance: Optional["PatientManager"] = None

    # Sinais globais do ciclo de vida do paciente
    patient_changed = QtCore.Signal(str)  # Emite o caminho absoluto do diretório do paciente
    patient_data_loaded = QtCore.Signal(dict)  # Emite o dicionário completo de dados (info.json)

    def __init__(self, project_service=None):
        if PatientManager._instance is not None:
            raise RuntimeError("PatientManager é um Singleton. Use PatientManager.get_instance()")

        super().__init__()
        self.project_service = project_service
        self._current_path: Optional[str] = None
        self._project_data: Dict[str, Any] = {}

        PatientManager._instance = self

    @classmethod
    def get_instance(cls, project_service=None) -> "PatientManager":
        """Retorna a instância única do PatientManager (Singleton)."""
        if cls._instance is None:
            if project_service is None:
                raise ValueError("ProjectServiceHomePage é obrigatório na primeira inicialização do PatientManager.")
            cls(project_service)
        return cls._instance

    @property
    def current_path(self) -> Optional[str]:
        """Retorna o caminho absoluto do paciente ativo atualmente."""
        return self._current_path

    @property
    def data(self) -> Dict[str, Any]:
        """Retorna o dicionário de dados atual do projeto/paciente."""
        return self._project_data

    def set_active_patient(self, path: str):
        """
        Define o paciente ativo, utiliza o ProjectService para carregar
        os dados do disco e dispara os sinais reativos para toda a aplicação.
        """
        if not path:
            return

        resolved_path = str(Path(path).resolve())

        # Evita reprocessamento redundante se o paciente já for o mesmo
        if self._current_path == resolved_path:
            return

        self._current_path = resolved_path

        # Carrega os dados via serviço de projetos injetado
        if self.project_service:
            self._project_data = self.project_service.load_project(Path(resolved_path)) or {}
        else:
            self._project_data = {}

        # Dispara os sinais notificando a mudança de estado
        self.patient_changed.emit(resolved_path)
        self.patient_data_loaded.emit(self._project_data)

    def save_current_data(self):
        """Salva o estado atual dos dados do paciente de volta no disco."""
        if not self._current_path or not self.project_service:
            return

        root = Path(self._current_path)
        self.project_service.save_project(root, self._project_data)

    def clear(self):
        """Limpa a sessão atual do paciente."""
        self._current_path = None
        self._project_data = {}
        self.patient_changed.emit("")