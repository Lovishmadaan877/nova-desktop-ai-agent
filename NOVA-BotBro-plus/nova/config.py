import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
SCREENSHOT_DIR = Path(os.getenv('NOVA_SCREENSHOT_DIR', DATA_DIR / 'screenshots'))
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = os.getenv('NOVA_DB_PATH', str(DATA_DIR / 'nova.db'))
OLLAMA_URL = os.getenv('NOVA_OLLAMA_URL', 'http://127.0.0.1:11434')
TEXT_MODEL = os.getenv('NOVA_TEXT_MODEL', 'llama3.2')
VISION_MODEL = os.getenv('NOVA_VISION_MODEL', 'llava')
MAX_STEPS = int(os.getenv('NOVA_MAX_STEPS', '15'))
MAX_RETRIES = int(os.getenv('NOVA_MAX_RETRIES', '2'))
ACTION_DELAY = float(os.getenv('NOVA_ACTION_DELAY', '0.20'))
REQUIRE_CONFIRMATION = os.getenv('NOVA_REQUIRE_CONFIRMATION', 'true').lower() == 'true'
