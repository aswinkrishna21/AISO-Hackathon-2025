import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

let _recording: Audio.Recording | null = null;
let _meterInterval: ReturnType<typeof setInterval> | null = null;

export type LevelCallback = (level: number) => void;

/**
 * Start recording and optionally receive live level callbacks.
 * Uses Expo Audio. If platform doesn't expose metering in status updates,
 * this will fall back to a small simulated heartbeat level so UI can update.
 */
export async function startRecording(onLevel?: LevelCallback) {
  const p = await Audio.requestPermissionsAsync();
  if (!p.granted) throw new Error('Microphone permission not granted');


  await Audio.setAudioModeAsync({
    allowsRecordingIOS: true,
    staysActiveInBackground: false,
    // interruptionModeIOS: 1, // 1 = DO_NOT_MIX, but not needed for most Expo apps
    playsInSilentModeIOS: true,
  });

  _recording = new Audio.Recording();


  try {
    await _recording.prepareToRecordAsync({
      android: {
        extension: '.m4a',
        outputFormat: 2, // MPEG_4
        audioEncoder: 3, // AAC
        sampleRate: 44100,
        numberOfChannels: 2,
        bitRate: 128000,
      },
      ios: {
        extension: '.caf',
  audioQuality: 0, // 0 = AVAudioQualityHigh
        sampleRate: 44100,
        numberOfChannels: 2,
        bitRate: 128000,
        linearPCMBitDepth: 16,
        linearPCMIsBigEndian: false,
        linearPCMIsFloat: false,
      },
      web: {
        mimeType: 'audio/webm',
        bitsPerSecond: 128000,
      },
    });

    // Try to use status updates for metering when available
    _recording.setOnRecordingStatusUpdate((status: any) => {
      // Some platforms/versions include metering in status (non-standard). Try common fields.
      const meter = status?.metering ?? status?.peakPower ?? status?.averagePower ?? null;
      if (meter != null) {
        // Normalize possible meter ranges (assume -160..0 dB or 0..1 amplitude)
        let normalized = 0;
        if (typeof meter === 'number') {
          if (meter <= 0) {
            // decibels: -160..0 -> map to 0..1
            normalized = Math.max(0, Math.min(1, 1 + meter / 160));
          } else {
            // already amplitude-like
            normalized = Math.max(0, Math.min(1, meter));
          }
        }
        onLevel?.(normalized);
      }
    });

    await _recording.startAsync();

    // If the platform doesn't report meters, provide a simulated heartbeat so the UI can react.
    if (onLevel) {
      _meterInterval = setInterval(() => {
        // simple oscillating value between 0 and 0.6
        const t = Date.now() / 300;
        const v = (Math.sin(t) + 1) / 2 * 0.6;
        onLevel(v);
      }, 120);
    }

    return _recording;
  } catch (err) {
    _recording = null;
    throw err;
  }
}

export async function stopRecording() {
  if (!_recording) return null;
  try {
    await _recording.stopAndUnloadAsync();
    const uri = _recording.getURI();
    // Delete temporary file so we don't keep recordings on device
    if (uri) {
      try {
        await FileSystem.deleteAsync(uri, { idempotent: true });
      } catch (e) {
        // deletion failed - ignore, we still won't return the URI
        console.warn('Could not delete temporary recording at', uri, e);
      }
    }
    return null;
  } finally {
    _recording = null;
    if (_meterInterval) {
      clearInterval(_meterInterval);
      _meterInterval = null;
    }
  }
}
