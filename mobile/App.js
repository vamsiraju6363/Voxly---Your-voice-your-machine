// App.js — Voxly mobile frontend (Expo / React Native)
// Press and hold the mic button to record, release to send.
// Shows transcript of what you said and the assistant's text reply.
// Auto-plays the spoken response.

import React, { useState, useRef, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { Audio } from "expo-av";
import * as FileSystem from "expo-file-system";
import { sendAudio } from "./api";

// Recording options producing mono 16 kHz WAV (Whisper friendly)
const RECORDING_OPTIONS = {
  android: {
    extension: ".wav",
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 128000,
    outputFormat: Audio.AndroidOutputFormat.DEFAULT,
    audioEncoder: Audio.AndroidAudioEncoder.DEFAULT,
  },
  ios: {
    extension: ".wav",
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 128000,
    audioQuality: Audio.IOSAudioQuality.HIGH,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
};

export default function App() {
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const soundRef = useRef(null);
  const scrollRef = useRef(null);

  // ------ Start recording on press-in ------
  const handlePressIn = useCallback(async () => {
    try {
      const { granted } = await Audio.requestPermissionsAsync();
      if (!granted) return;

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording: rec } = await Audio.Recording.createAsync(
        RECORDING_OPTIONS
      );
      setRecording(rec);
      setIsRecording(true);
    } catch (err) {
      console.warn("Mic error:", err);
    }
  }, []);

  // ------ Stop recording & send to backend on release ------
  const handlePressOut = useCallback(async () => {
    setIsRecording(false);
    if (!recording) return;

    try {
      await recording.stopAndUnloadAsync();
    } catch {
      // Already stopped
    }

    const uri = recording.getURI();
    setRecording(null);
    if (!uri) return;

    setLoading(true);
    try {
      const result = await sendAudio(uri, sessionId);

      // Persist session ID across calls
      if (result.sessionId && !sessionId) {
        setSessionId(result.sessionId);
      }

      // Append transcript + reply to chat history
      const newMessages = [];
      if (result.transcript) {
        newMessages.push({ type: "user", text: result.transcript });
      }
      if (result.reply) {
        newMessages.push({ type: "assistant", text: result.reply });
      }
      setMessages((prev) => {
        const updated = [...prev, ...newMessages];
        // Auto-scroll after state update
        setTimeout(() => scrollRef.current?.scrollToEnd?.({ animated: true }), 100);
        return updated;
      });

      // Save WAV to cache & auto-play
      if (result.audioBase64) {
        const fileUri = FileSystem.cacheDirectory + "voxly_response.wav";
        await FileSystem.writeAsStringAsync(fileUri, result.audioBase64, {
          encoding: FileSystem.EncodingType.Base64,
        });
        await playAudio(fileUri);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { type: "assistant", text: `Error: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }, [recording, sessionId]);

  // ------ Play a local WAV file ------
  const playAudio = async (fileUri) => {
    try {
      if (soundRef.current) {
        await soundRef.current.unloadAsync();
        soundRef.current = null;
      }
      const { sound } = await Audio.Sound.createAsync({ uri: fileUri });
      soundRef.current = sound;
      await sound.playAsync();
    } catch (err) {
      console.warn("Playback error:", err);
    }
  };

  // ------ Render ------
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <Text style={styles.title}>Voxly</Text>
      <Text style={styles.subtitle}>Your voice, your machine</Text>

      {/* Chat history */}
      <ScrollView
        ref={scrollRef}
        style={styles.chat}
        contentContainerStyle={styles.chatContent}
      >
        {messages.length === 0 && (
          <Text style={styles.placeholder}>
            Press and hold the mic button to speak...
          </Text>
        )}
        {messages.map((msg, i) => (
          <View
            key={i}
            style={[
              styles.bubble,
              msg.type === "user" ? styles.userBubble : styles.assistantBubble,
            ]}
          >
            <Text style={styles.bubbleLabel}>
              {msg.type === "user" ? "You" : "Assistant"}
            </Text>
            <Text style={styles.bubbleText}>{msg.text}</Text>
          </View>
        ))}
      </ScrollView>

      {/* Mic button */}
      <TouchableOpacity
        style={[styles.micButton, isRecording && styles.micActive]}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        disabled={loading}
        activeOpacity={0.7}
      >
        <Text style={styles.micIcon}>
          {loading ? "⏳" : isRecording ? "🔴" : "🎤"}
        </Text>
        <Text style={styles.micLabel}>
          {loading ? "Thinking..." : isRecording ? "Release to send" : "Hold to talk"}
        </Text>
      </TouchableOpacity>
    </KeyboardAvoidingView>
  );
}

// ------ Styles ------
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0d0d1a",
    paddingHorizontal: 16,
    paddingTop: 50,
    paddingBottom: 20,
  },
  title: {
    color: "#e94560",
    fontSize: 30,
    fontWeight: "800",
    textAlign: "center",
    letterSpacing: 2,
  },
  subtitle: {
    color: "#555",
    fontSize: 13,
    textAlign: "center",
    marginBottom: 16,
  },
  chat: {
    flex: 1,
  },
  chatContent: {
    paddingVertical: 8,
  },
  placeholder: {
    color: "#444",
    textAlign: "center",
    marginTop: 60,
    fontSize: 15,
  },
  bubble: {
    padding: 12,
    borderRadius: 14,
    marginVertical: 4,
    maxWidth: "82%",
  },
  userBubble: {
    backgroundColor: "#162447",
    alignSelf: "flex-end",
  },
  assistantBubble: {
    backgroundColor: "#1a1a3e",
    alignSelf: "flex-start",
    borderWidth: 1,
    borderColor: "#2a2a5e",
  },
  bubbleLabel: {
    color: "#e94560",
    fontSize: 11,
    fontWeight: "700",
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  bubbleText: {
    color: "#e0e0e0",
    fontSize: 15,
    lineHeight: 21,
  },
  micButton: {
    backgroundColor: "#162447",
    paddingVertical: 18,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: "#1e3a6e",
  },
  micActive: {
    backgroundColor: "#e94560",
    borderColor: "#ff6b81",
  },
  micIcon: {
    fontSize: 26,
  },
  micLabel: {
    color: "#ccc",
    fontSize: 13,
    marginTop: 4,
    fontWeight: "600",
  },
});
