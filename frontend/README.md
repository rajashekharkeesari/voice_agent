# Hospital Voice Assistant — Frontend

A browser client for the voice agent. It:

1. Records microphone audio in the browser.
2. Streams the audio to the Pipecat bot over WebRTC (`SmallWebRTCTransport`).
3. The bot runs the pipeline: **Deepgram STT → LangGraph → Cartesia TTS**.
4. Shows a live chat of the **human** and **AI** turns from transcript events.
5. Plays the AI's spoken (TTS) response back through a hidden `<audio>` element.

```
Browser mic ──WebRTC──▶ Pipecat (STT) ──▶ LangGraph ──▶ Pipecat (TTS) ──WebRTC──▶ Browser speaker
     ▲                                                                                  │
     └──────────────── transcript events render the chat UI ◀───────────────────────────┘
```

## Prerequisites

- Node.js 18+
- The Pipecat bot running locally (see `backend/pipecat/voice_to_text.py`)

## Run the bot (backend)

The bot uses the Pipecat development runner, which serves the WebRTC offer
endpoint at `http://localhost:7860`. From the `backend` folder, with your
`.env` populated (`DEEPGRAM_API_KEY`, `CARTESIA_API_KEY`, etc.):

```powershell
python -m pipecat.voice_to_text
```

> The bot must expose the SmallWebRTC server transport (the default dev runner
> does). The frontend posts its WebRTC offer to `/api/offer`.

## Run the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, click **Start**, allow microphone access, and talk.

The dev server proxies `/api` → `http://localhost:7860`, so the browser reaches
the bot without CORS issues. If your bot runs on a different host/port, change
the proxy target in `vite.config.js`.

## Build for production

```powershell
npm run build
npm run preview
```

## Files

| File             | Purpose                                                      |
| ---------------- | ------------------------------------------------------------ |
| `index.html`     | Markup: chat area, status indicator, Start/Mute controls.    |
| `src/main.js`    | PipecatClient + SmallWebRTC wiring, transcript → chat, audio. |
| `src/style.css`  | Chat bubble + control styling.                               |
| `vite.config.js` | Dev server + `/api` proxy to the bot.                        |

## Notes

- Mic recording and WebRTC negotiation are handled by the Pipecat SDK
  (`enableMic: true`). The browser prompts for mic permission on **Start**.
- The chat is driven by `onUserTranscript` (your speech) and `onBotTranscript`
  (the assistant's reply). Partial user transcripts render dimmed/italic until
  finalized.
