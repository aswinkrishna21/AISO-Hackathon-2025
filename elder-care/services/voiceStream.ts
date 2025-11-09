import { PermissionsAndroid, Platform } from 'react-native';

let ws: WebSocket | null = null;

let ws_endpoint = 'wss://8387f03c1ca7.ngrok-free.app/ws';
async function requestAudioPermission(){
    if (Platform.OS === 'android') {
    const granted = await PermissionsAndroid.request(
      PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
      {
        title: 'Microphone Permission',
        message: 'App needs access to your microphone to record audio.',
        buttonNeutral: 'Ask Me Later',
        buttonNegative: 'Cancel',
        buttonPositive: 'OK',
      }
    );
    return granted === PermissionsAndroid.RESULTS.GRANTED;
  }
  return true; 
}

// export async function startStreaming() {
//   // 1️⃣ Connect to FastAPI WebSocket
//   ws = new WebSocket('wss://8387f03c1ca7.ngrok-free.app/ws');

//   ws.onopen = () => console.log('WebSocket connected');
//   ws.onerror = (e) => console.log('WebSocket error', e);
//   ws.onclose = () => console.log('WebSocket closed');

//   // 2️⃣ Configure AudioRecord

//     const hasPermission = await requestAudioPermission();
//     if (!hasPermission) {
//       console.warn('Microphone permission denied');
//       return;
//     }
//     AudioRecord.init({
//       sampleRate: 16000,
//       channels: 1,
//       bitsPerSample: 16,
//       audioSource: 6,
//         wavFile: 'audio.wav',
//         // bufferSize: 2048,
//       });


//   console.log('AudioRecord initialized:', AudioRecord);
//   // 3️⃣ Start recording
//   AudioRecord.start();
//       console.log('Audio recording started');
//   // 4️⃣ Send each chunk to server
//     AudioRecord.on('data', data => {
//     if (ws?.readyState === WebSocket.OPEN) {
//         const message = JSON.stringify({ audio: data });
//         ws.send(message);
//     }
//     });

// }

// export async function stopStreaming() {
//   AudioRecord.stop();
//   if (ws) {
//     ws.close();
//     ws = null;
//   }
// }
// services/voiceStream.ts
import { PipecatClient, PipecatClientOptions } from '@pipecat-ai/client-js';
import { DailyTransport } from '@pipecat-ai/daily-transport';

let pcClient: PipecatClient | null = null;

/**
 * Start Pipecat streaming with DailyTransport
 */
export async function startStreaming() {
  try {
    if (pcClient) return; // already running

    const transport = new DailyTransport(); // RN-compatible transport

    const clientOptions: PipecatClientOptions = {
      transport,
      enableMic: true,   // capture microphone
      enableCam: false,  // no video
      callbacks: {
        onConnected: () => console.log('✅ Connected to bot'),
        onDisconnected: () => console.log('❌ Disconnected'),
        onBotReady: (data) => console.log('🤖 Bot ready', data),
        onUserTranscript: (data) => {
          if (data.final) console.log('🗣 User:', data.text);
        },
        onBotTranscript: (data) => console.log('🤖 Bot:', data.text),
        onError: (err) => console.error('Error:', err),
      },
    };

    pcClient = new PipecatClient(clientOptions);
    // expose globally for debugging
    // @ts-ignore
    global.pcClient = pcClient;

    console.log('Initializing devices...');
    await pcClient.initDevices(); // requests microphone permission and sets up tracks

    console.log('Connecting to bot...');
    await pcClient.startBotAndConnect({
      endpoint: ws_endpoint, // your FastAPI Pipecat server
    });

    console.log('🎉 Streaming started');
  } catch (err) {
    console.error('Failed to start streaming:', err);
  }
}

/**
 * Stop streaming and clean up
 */
export async function stopStreaming() {
  if (pcClient) {
    try {
      await pcClient.disconnect();
      pcClient = null;
      console.log('🛑 Streaming stopped');
    } catch (err) {
      console.error('Error stopping streaming:', err);
    }
  }
}
