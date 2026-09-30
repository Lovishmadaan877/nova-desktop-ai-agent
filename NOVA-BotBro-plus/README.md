# NOVA — Autonomous Windows Desktop AI Agent

NOVA is a local-first Windows computer-use agent built around:

**Observe → Plan → Act → Verify → Recover**

It combines an LLM planner, vision-based UI grounding, OCR fallback, PyAutoGUI control, safety gates, persistent task history, bounded retries, and final-state verification.

## What makes the project resume-worthy

- **LLM planning:** converts natural-language goals into validated action plans.
- **Vision grounding:** identifies UI targets from screenshots instead of relying only on fixed coordinates.
- **Computer control:** executes mouse, keyboard, application-launch, and drawing actions.
- **Recovery:** captures the failure state and asks the planner for a revised plan.
- **Verification:** checks the final screen before NOVA claims task success.
- **Safety:** uses an application allowlist, blocks sensitive goals without explicit confirmation, and never exposes a shell-command action to the planner.
- **Persistence:** stores task status, timestamps, and results in SQLite.
- **Local-first AI:** supports Ollama models without requiring a cloud LLM API.

## Example tasks

- Open Paint and draw a lion sketch.
- Open Calculator and calculate `345 * 782`.
- Open Notepad and write a study plan.
- Interact with visible UI elements using semantic targets such as `Save button` when the vision model can ground them.

## Architecture

```text
User / Web UI
     │
     ▼
 FastAPI Task API
     │
     ▼
 Orchestrator
 ┌───┼───────────────┐
 ▼   ▼               ▼
LLM Vision        Safety
Plan Grounding     Gates
 │      │             │
 └──────┼─────────────┘
        ▼
   PyAutoGUI Executor
        │
        ▼
    Windows UI
        │
        ▼
 Screenshot / Vision
        │
   ┌────┴────┐
   ▼         ▼
Verify     Recover
   │         │
   └────┬────┘
        ▼
   SQLite History
```

## Tech stack

Python, FastAPI, Pydantic, Ollama, LLaVA, OpenCV, Tesseract OCR, PyAutoGUI, SQLite, pytest.

## Setup

Windows 10/11 and Python 3.11+ are recommended.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Then open `http://127.0.0.1:8000` or `http://127.0.0.1:8000/docs`.

## Local AI models

Install Ollama and pull the default models:

```powershell
ollama pull llama3.2
ollama pull llava
```

The model names and Ollama URL can be changed in `.env`.

## Configuration

Important settings include:

- `NOVA_MAX_STEPS` — execution bound.
- `NOVA_MAX_RETRIES` — recovery bound.
- `NOVA_REQUIRE_CONFIRMATION` — safety confirmation switch.
- `NOVA_SCREENSHOT_DIR` — screenshot output directory.
- `NOVA_DB_PATH` — SQLite database path.

## Safety design

NOVA uses an explicit Windows application allowlist and does **not** expose `cmd.exe`, PowerShell, or arbitrary shell execution as an agent action. Potentially sensitive goals such as deletion, purchasing, credentials, shutdown, and formatting require explicit confirmation when the safety setting is enabled.

The project is intended for controlled local automation. Test it on a non-critical Windows environment and avoid granting it access to sensitive accounts or destructive workflows.

## Testing

Run:

```powershell
pytest -q
```

The test suite covers fallback planning, safety allowlisting, and Pydantic model behavior without launching real desktop applications.

## Portfolio note

NOVA is an original implementation of a local computer-use-agent system. The project demonstrates AI orchestration, computer vision, automation, API design, safety controls, persistence, recovery, and verification in one system.
