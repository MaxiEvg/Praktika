from pathlib import Path
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent  # Путь к папке admin
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))