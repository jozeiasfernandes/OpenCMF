import subprocess
import sys
from pathlib import Path


def capture_toolbar_screenshot(py_file: Path) -> bool:
    """Captura a toolbar e salva um .png com o mesmo nome na mesma pasta."""
    png_path = py_file.with_suffix(".png")

    # Este é o script interno que roda isolado para não poluir o processo principal
    capture_script = f"""
import sys, inspect, importlib.util
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap, QPainter

app = QApplication.instance() or QApplication(sys.argv)
spec = importlib.util.spec_from_file_location("_mod", r"{py_file}")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

widgets = []
for name, obj in inspect.getmembers(mod, inspect.isclass):
    if issubclass(obj, QWidget) and obj.__module__ == "_mod":
        try:
            instance = obj()
            instance.show()
            widgets.append(instance)
        except: pass

def capture():
    if widgets:
        # Pega a primeira widget válida encontrada como toolbar
        widgets[0].grab().save(r"{png_path}", "PNG")
    app.quit()

QTimer.singleShot(500, capture)
app.exec()
"""
    try:
        subprocess.run([sys.executable, "-c", capture_script], timeout=15, check=True)
        return png_path.exists()
    except Exception:
        return False