import VoiceButton from '@/components/voice_button';
import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

export default function HomeScreen() {
  const [isListening, setIsListening] = useState(false);

  return (
    <View style={{height: '100%', justifyContent: 'center', alignItems: 'center'}}>
      <Text>Hello</Text>
      <VoiceButton listening={isListening} onStart={() => setIsListening(true)} onStop={() => setIsListening(false)} />
    </View>
  );
}

const styles = StyleSheet.create({
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stepContainer: {
    gap: 8,
    marginBottom: 8,
  },
  reactLogo: {
    height: 178,
    width: 290,
    bottom: 0,
    left: 0,
    position: 'absolute',
  },
  text: {
    color: 'white',
  }
});
