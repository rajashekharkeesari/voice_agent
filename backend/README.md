# Voice Agent — Backend

Hospital voice assistant. Audio flows:

```
Browser mic ─WebRTC─▶ pipecat (Deepgram STT) ─▶ LangGraph ─▶ pipecat (Cartesia TTS) ─WebRTC─▶ Browser
                                                   │
                                     tools over MCP (HTTP :8000)
                                                   │
                              services ─▶ repositories ─▶ SQLAlchemy ─▶ SQLite
```

## Requirements

- **Python 3.12** (pipecat supports 3.10–3.13; it does NOT install on 3.14).
  The `voice_agent/` virtualenv in the project root is built on 3.12.
- API keys for OpenAI (LLM), Deepgram (STT), Cartesia (TTS).

## Install

```powershell
# from the project root
.\voice_agent\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Configure

Edit `backend/.env`. Pick an LLM provider with `LLM_PROVIDER` and set the
STT/TTS keys:

```
# --- LLM: choose Llama / Qwen / OpenAI ---
# Local Llama/Qwen via Ollama (no key):
LLM_PROVIDER = ollama
LLM_MODEL    = llama3.1          # or qwen2.5, llama3.2, qwen2.5:14b, ...

# OR hosted Llama/Qwen via Groq (fast):
# LLM_PROVIDER = groq
# LLM_MODEL    = llama-3.3-70b-versatile   # or qwen-2.5-32b
# GROQ_API_KEY = gsk_...

# OR any OpenAI-compatible server (vLLM / Together / OpenRouter / LM Studio):
# LLM_PROVIDER = openai_compatible
# LLM_MODEL    = meta-llama/Llama-3.1-8B-Instruct
# LLM_BASE_URL = http://localhost:8001/v1
# LLM_API_KEY  = ...

# OR OpenAI:
# LLM_PROVIDER = openai
# LLM_MODEL    = gpt-4o-mini
# OPENAI_API_KEY = sk-...

# --- Voice (required for the bot) ---
DEEPGRAM_API_KEY = ...
CARTESIA_API_KEY = ...
# sql_connection, LLM_TEMPERATURE, MCP_SERVER_URL have sensible defaults
```

### Using Llama / Qwen locally with Ollama

```powershell
# install Ollama from https://ollama.com, then:
ollama pull llama3.1      # or: ollama pull qwen2.5
ollama serve              # usually already running as a service
```

Set `LLM_PROVIDER = ollama` and `LLM_MODEL = llama3.1` (or `qwen2.5`). No key
needed. For reliable **tool calling** (the MCP hospital tools), use a
tool-capable model such as `llama3.1`, `llama3.3`, or `qwen2.5`.

## Initialize the database (once)

```powershell
.\voice_agent\Scripts\python.exe -m backend.main
```

Creates the SQLite tables (`voice_agent.db`).

## Run (three processes)

Run each from the **project root** so `backend.*` imports resolve.

1. MCP tool server (doctors, appointments, patients, hospital info):
   ```powershell
   .\voice_agent\Scripts\python.exe -m backend.mcp_server.mcp
   ```
   Serves `http://127.0.0.1:8000/mcp`.

2. Voice bot (STT → LangGraph → TTS):
   ```powershell
   .\voice_agent\Scripts\python.exe -m backend.pipecat.voice_to_text
   ```
   Pipecat's dev runner serves the WebRTC offer endpoint (default port 7860).

3. Frontend: see `../frontend` (`npm run dev`).

## Architecture

| Layer            | Location                      | Role                                             |
| ---------------- | ----------------------------- | ------------------------------------------------ |
| Voice pipeline   | `pipecat/voice_to_text.py`    | STT → LangGraph → TTS, SmallWebRTC transport     |
| Graph            | `Graph/workflow.py`           | `compiled_graph`: streams `{"input": text}` → reply chunks |
| Streaming        | `nodes/streaming.py`          | `astream_answer`: yields reply tokens as generated |
| Nodes            | `nodes/`                      | supervisor / appointment / routing               |
| Agents           | `agents/`                     | ReAct agents over the LLM + MCP tools            |
| State            | `states/`                     | `HospitalState`, `AppointmentState`, `SupervisorState` |
| LLM              | `LLM/llm.py`                  | lazy `ChatOpenAI` (`get_llm()`)                  |
| MCP server       | `mcp_server/`                 | FastMCP tools over HTTP                           |
| MCP client       | `mcp_client/client.py`        | loads MCP tools as LangChain tools               |
| Services         | `services/`                   | business logic                                   |
| Repositories     | `Repositories/`               | data access                                      |
| Models / DB      | `models/`, `db/connection.py` | SQLAlchemy ORM over SQLite                        |

## Streaming (incremental voice)

The assistant speaks **while it is generating**, not after. The LLM runs with
`streaming=True`, and `compiled_graph.astream({"input": text})` yields reply
chunks as the model produces them. pipecat's `LangchainProcessor` pushes each
chunk to Cartesia TTS immediately, so audio starts playing on the first few
words and streams to the browser over WebRTC with low latency. For tool-using
turns, only the final spoken answer is streamed (tool-call planning chunks are
skipped).

## Receptionist flow

A single receptionist agent ("Mia") runs the whole call like a front desk:

1. Greets and asks how it can help.
2. **Identifies** the caller by phone number + name (`identify_patient`). If
   found, greets by name; if not, offers to register (`register_patient`).
3. Asks the **reason for the call** and classifies it into
   `book | reschedule | cancel | availability | other`.
4. Runs the matching sub-flow **one question at a time** (doctor → date →
   slot, etc.), using the tools to resolve names/slots.
5. **Reads the details back and waits for a clear "yes"** before booking,
   rescheduling, or cancelling, then confirms the result.

### State that updates from both patient and AI turns

The agent keeps a structured per-call state (`call_states` table) via the
`update_call_state` / `get_call_state` tools. As the patient speaks and the
agent decides things, it records identity, `reason_for_call`, `call_type`, and
the booking slots. This state is keyed by the caller's `thread_id` and lives in
the DB, so it accumulates across turns and can be read back for confirmation.

### Memory

- **Conversation memory:** a LangGraph checkpointer gives the agent the running
  message history each turn, keyed by `thread_id` (the pipecat participant id).
- **Persistent memory:** a `SqliteSaver` writes that history to disk
  (`CHECKPOINT_DB`, default `receptionist_memory.sqlite`), so an interrupted
  call can resume. Falls back to in-memory if the sqlite saver isn't installed.

## Appointment tools: book, reschedule, cancel

The agent has tools to run the whole appointment lifecycle from natural speech:

- `find_doctor_by_name` / `find_patient_by_name` — resolve spoken names to IDs
- `list_available_slots(doctor_id, date)` — discover open slots
- `book_appointment` — reserves the slot (marks it booked)
- `reschedule_appointment(appointment_id, new_slot_id[, new_date])` — frees the
  old slot and books the new one
- `cancel_appointment` — frees the slot again
- `get_patient_appointments`, `register_patient`, `find_patient_by_phone`, ...

**Multi-turn memory:** the agent uses a LangGraph `MemorySaver` checkpointer and
threads each caller's conversation by participant id. So a booking can be
collected across turns ("I'd like an appointment" → "with Dr. Smith" →
"tomorrow at 3") because the agent remembers the earlier turns.

## Tests

A success/fail matrix for AI↔patient conversations (book, reschedule, cancel,
conflict handling, name lookups, routing) runs against an isolated in-memory DB:

```powershell
.\voice_agent\Scripts\python.exe -m pytest
```

## Notes

- The LangGraph compiles and the bot imports even without API keys (the LLM is
  created lazily, only needed when actually answering).
- If the MCP server is down, the agent degrades gracefully and answers without
  external tools.
- **Windows + WebRTC:** pipecat's SmallWebRTC transport is best supported on
  macOS/Linux. On Windows, running the voice bot under WSL2 is recommended if
  you hit native WebRTC issues.
