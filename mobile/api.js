// api.js — talks to the Voxly backend over HTTP
// Sends recorded audio and receives a WAV audio response + transcripts.

import { API_URL } from "./config";

/** Convert an ArrayBuffer to a base64 string (React Native safe). */
function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  const chunks = [];
  const chunkSize = 0x8000; // 32 kB chunks to avoid stack overflow
  for (let i = 0; i < bytes.length; i += chunkSize) {
    const chunk = bytes.subarray(i, i + chunkSize);
    chunks.push(String.fromCharCode.apply(null, chunk));
  }
  return btoa(chunks.join(""));
}

/**
 * Send an audio recording to the backend and get the assistant's audio reply.
 *
 * @param {string} audioUri  - Local file URI of the recording (from expo-av).
 * @param {string} sessionId - Current session ID (null for new session).
 * @returns {{ transcript, reply, sessionId, audioBase64 }}
 */
export async function sendAudio(audioUri, sessionId) {
  // Build multipart form data
  const formData = new FormData();
  formData.append("audio", {
    uri: audioUri,
    type: "audio/wav",
    name: "recording.wav",
  });

  const url = sessionId
    ? `${API_URL}/chat?session_id=${encodeURIComponent(sessionId)}`
    : `${API_URL}/chat`;

  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || "Request failed");
  }

  // Extract metadata from custom headers
  const transcript = response.headers.get("X-Transcript") || "";
  const reply = response.headers.get("X-Reply") || "";
  const newSessionId = response.headers.get("X-Session-ID") || sessionId;

  // Convert WAV response to base64 for local file playback
  const buffer = await response.arrayBuffer();
  const audioBase64 = arrayBufferToBase64(buffer);

  return { transcript, reply, sessionId: newSessionId, audioBase64 };
}
