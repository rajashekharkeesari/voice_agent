import { PipecatClient, RTVIEvent } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";

// ---------------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------------
const chatEl = document.getElementById("chat");
const emptyStateEl = document.getElementById("empty-state");
const connectBtn = document.getElementById("connect-btn");
const micBtn = document.getElementById("mic-btn");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");
const levelFill = document.getElementById("level-fill");
const botAudio = document.getElementById("bot-audio");

// Endpoint the Pipecat SmallWebRTC server exposes for the WebRTC offer.
// Vite proxies /api -> http://localhost:7860 (see vite.config.js).
const OFFER_ENDPOINT = "/api/offer";

// ---------------------------------------------------------------------------
// Chat rendering
// ---------------------------------------------------------------------------
// We keep a reference to the "live" message bubble for each role so that
// streamed/partial transcripts update in place instead of creating a new
// bubble for every token.
let liveUserBubble = null;
let liveBotBubble = null;

function hideEmptyState() {
  if (emptyStateEl) emptyStateEl.style.display = "none";
}

function createBubble(role) {
  hideEmptyState();
  const row = document.createElement("div");
  row.className = `msg ${role}`;

  const who = document.createElement("span");
  who.className = "who";
  who.textContent = role === "user" ? "You" : "Assistant";

  const text = document.createElement("div");
  text.className = "text";

  row.appendChild(who);
  row.appendChild(text);
  chatEl.appendChild(row);
  chatEl.scrollTop = chatEl.scrollHeight;
  return text;
}

function appendUserTranscript(data) {
  // data: { text, final, timestamp, user_id }
  if (!data.text) return;
  if (!liveUserBubble) {
    liveUserBubble = createBubble("user");
  }
  liveUserBubble.textContent = data.text;
  liveUserBubble.parentElement.classList.toggle("partial", !data.final);
  chatEl.scrollTop = chatEl.scrollHeight;

  // Once the user turn is final, close the bubble so the next utterance
  // starts a fresh one.
  if (data.final) {
    liveUserBubble = null;
  }
}

function appendBotTranscript(data) {
  // data: { text }  — finalized bot output, sentence aggregated.
  if (!data.text) return;
  if (!liveBotBubble) {
    liveBotBubble = createBubble("bot");
    liveBotBubble.textContent = data.text;
  } else {
    // Bot sentences arrive one at a time; join them in the same turn.
    liveBotBubble.textContent =
      `${liveBotBubble.textContent} ${data.text}`.trim();
  }
  chatEl.scrollTop = chatEl.scrollHeight;
}

// ---------------------------------------------------------------------------
// Status helpers
// ---------------------------------------------------------------------------
function setStatus(state, label) {
  statusDot.dataset.state = state; // styled via CSS
  statusText.textContent = label;
}

// ---------------------------------------------------------------------------
// Pipecat client
// ---------------------------------------------------------------------------
const pcClient = new PipecatClient({
  transport: new SmallWebRTCTransport(),
  enableMic: true, // record and stream the microphone
  enableCam: false,
  callbacks: {
    onConnected: () => setStatus("connecting", "Connected"),
    onBotReady: () => {
      setStatus("connected", "Listening");
      micBtn.disabled = false;
    },
    onDisconnected: () => {
      setStatus("idle", "Disconnected");
      micBtn.disabled = true;
      liveUserBubble = null;
      liveBotBubble = null;
      levelFill.style.width = "0%";
    },
    onBotStartedSpeaking: () => setStatus("speaking", "Assistant speaking"),
    onBotStoppedSpeaking: () => setStatus("connected", "Listening"),
    onUserStartedSpeaking: () => {
      // Starting a new user turn ends the previous bot turn.
      liveBotBubble = null;
    },

    // Transcript events drive the chat UI.
    onUserTranscript: (data) => appendUserTranscript(data),
    onBotTranscript: (data) => appendBotTranscript(data),

    // Local mic level -> meter
    onLocalAudioLevel: (level) => {
      levelFill.style.width = `${Math.min(100, Math.round(level * 100))}%`;
    },

    onError: (message) => {
      console.error("[pipecat error]", message);
      setStatus("error", "Error — see console");
    },
  },
});

// Play the bot's audio track through the hidden <audio> element.
pcClient.on(RTVIEvent.TrackStarted, (track, participant) => {
  if (participant?.local || track.kind !== "audio") return;
  const stream = new MediaStream([track]);
  botAudio.srcObject = stream;
  botAudio.play().catch((e) => console.warn("Audio playback blocked:", e));
});

// ---------------------------------------------------------------------------
// Connection lifecycle
// ---------------------------------------------------------------------------
let connected = false;

async function connect() {
  try {
    connectBtn.disabled = true;
    setStatus("connecting", "Connecting…");

    // Initialize local media (prompts for mic permission) then negotiate
    // the WebRTC connection with the Pipecat bot.
    await pcClient.connect({
      webrtcRequestParams: { endpoint: OFFER_ENDPOINT },
    });

    connected = true;
    connectBtn.textContent = "Stop";
    connectBtn.classList.remove("primary");
    connectBtn.classList.add("danger");
  } catch (e) {
    console.error("Failed to connect:", e);
    setStatus("error", "Connection failed");
  } finally {
    connectBtn.disabled = false;
  }
}

async function disconnect() {
  try {
    connectBtn.disabled = true;
    await pcClient.disconnect();
  } catch (e) {
    console.error("Error during disconnect:", e);
  } finally {
    connected = false;
    connectBtn.textContent = "Start";
    connectBtn.classList.add("primary");
    connectBtn.classList.remove("danger");
    connectBtn.disabled = false;
  }
}

connectBtn.addEventListener("click", () => {
  if (connected) {
    disconnect();
  } else {
    connect();
  }
});

// ---------------------------------------------------------------------------
// Mic mute toggle
// ---------------------------------------------------------------------------
let micMuted = false;
micBtn.addEventListener("click", () => {
  micMuted = !micMuted;
  pcClient.enableMic(!micMuted);
  micBtn.textContent = micMuted ? "Unmute mic" : "Mute mic";
  micBtn.classList.toggle("muted", micMuted);
});

// Clean up the connection if the tab is closed.
window.addEventListener("beforeunload", () => {
  if (connected) pcClient.disconnect();
});

setStatus("idle", "Disconnected");
