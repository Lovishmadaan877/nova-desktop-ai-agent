import base64
import json
import re
from pathlib import Path

import cv2
import pytesseract
import requests

from .config import OLLAMA_URL, VISION_MODEL

class Vision:
    def ocr(self, path):
        im = cv2.imread(str(path))
        if im is None:
            return ''
        try:
            return pytesseract.image_to_string(im).strip()[:5000]
        except Exception:
            return ''

    def analyze(self, path, question='Describe the visible Windows UI and identify useful clickable targets.'):
        path = Path(path)
        raw = base64.b64encode(path.read_bytes()).decode()
        prompt = (
            f'You are NOVA screen grounding. {question} '
            'Return ONLY JSON with keys description and targets. '
            'targets is an array of {label,x,y,confidence}. '
            'Coordinates are absolute screenshot pixels.'
        )
        try:
            r = requests.post(
                f'{OLLAMA_URL}/api/generate',
                json={'model': VISION_MODEL, 'prompt': prompt, 'images': [raw], 'stream': False},
                timeout=90,
            )
            r.raise_for_status()
            return self._json(r.json().get('response', ''))
        except Exception:
            return {
                'description': 'Vision model unavailable; OCR fallback used.',
                'targets': [],
                'ocr': self.ocr(path),
            }

    def find_target(self, path, label):
        d = self.analyze(path, f"Find the UI element matching '{label}'.")
        for target in d.get('targets', []):
            if label.lower() in str(target.get('label', '')).lower():
                try:
                    return int(target['x']), int(target['y']), float(target.get('confidence', 0))
                except Exception:
                    pass
        return None

    def verify_goal(self, path, goal):
        """Ask the vision model whether the final screen demonstrates goal completion.
        Returns None when verification cannot be performed rather than falsely claiming success.
        """
        path = Path(path)
        raw = base64.b64encode(path.read_bytes()).decode()
        prompt = (
            'You are the final verifier for a Windows desktop automation agent. '
            f'User goal: {goal}\n'
            'Inspect the screenshot and decide whether the visible state demonstrates that the goal was completed. '
            'Return ONLY JSON: {"success":true|false,"evidence":"short explanation"}. '
            'Do not assume an action succeeded merely because it was attempted.'
        )
        try:
            r = requests.post(
                f'{OLLAMA_URL}/api/generate',
                json={'model': VISION_MODEL, 'prompt': prompt, 'images': [raw], 'stream': False},
                timeout=90,
            )
            r.raise_for_status()
            data = self._json(r.json().get('response', ''))
            if isinstance(data.get('success'), bool):
                return data
        except Exception:
            return None
        return None

    def _json(self, text):
        text = re.sub(r'^```(?:json)?', '', text.strip(), flags=re.I).strip()
        text = re.sub(r'```$', '', text).strip()
        a, b = text.find('{'), text.rfind('}')
        if a < 0 or b < 0:
            raise ValueError('No vision JSON')
        return json.loads(text[a:b + 1])
