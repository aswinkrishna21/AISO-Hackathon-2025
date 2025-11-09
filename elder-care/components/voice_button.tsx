import { startStreaming, stopStreaming } from '@/services/voiceStream';
import { Ionicons } from '@expo/vector-icons';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Animated, Pressable, StyleSheet, Text, View, ViewStyle } from 'react-native';
// import RTCView from 'react-native-webrtc/lib/typescript/RTCView';

type Props = {
	listening?: boolean;
	onStart?: () => void;
	onStop?: () => void;
	size?: number;
	style?: ViewStyle;
};

export default function VoiceButton({ listening: listeningProp, onStart, onStop, size = 72, style }: Props) {
	const [internalListening, setInternalListening] = useState(false);
	const listening = typeof listeningProp === 'boolean' ? listeningProp : internalListening;

	const scale = useRef(new Animated.Value(1)).current;


	useEffect(() => {
		Animated.spring(scale, {
			toValue: listening ? 0.92 : 1,
			useNativeDriver: true,
			mass: 1,
			stiffness: 200,
			damping: 20,
		}).start();
	}, [listening]);

	const toggle = useCallback(async () => {
		const isControlled = typeof listeningProp === 'boolean';

		const start = async () => {
			try {
				await startStreaming();
                console.log('VoiceButton: started streaming');
			} catch (e) {
				console.warn('startStreaming failed', e);
			}
			onStart?.();
		};

		const stop = async () => {
			try {
				await stopStreaming();
			} catch (e) {
				// ignore
			}
			onStop?.();
			console.log('VoiceButton: stopped streaming');
		};

		if (isControlled) {
			if (listening) stop();
			else start();
		} else {
			setInternalListening((prev) => {
				const next = !prev;
				(async () => (next ? start() : stop()))();
				return next;
			});
		}
	}, [listeningProp, listening, onStart, onStop]);

	const onPressIn = useCallback(() => {
		Animated.spring(scale, { toValue: 0.96, useNativeDriver: true }).start();
	}, []);

	const onPressOut = useCallback(() => {
		Animated.spring(scale, { toValue: listening ? 0.92 : 1, useNativeDriver: true }).start();
	}, [listening]);

	const backgroundColor = listening ? '#FF4D4D' : '#007AFF';
	const iconName = listening ? 'mic' : 'mic-outline';

	return (
		<View style={[{ flexDirection: 'row', alignItems: 'center', justifyContent: 'center' }]}>
			<Pressable
				onPress={toggle}
				onPressIn={onPressIn}
				onPressOut={onPressOut}
				accessibilityLabel={listening ? 'Stop streaming' : 'Start streaming'}
				accessibilityRole="button"
				style={[{ width: size, height: size, borderRadius: size / 2 }, style]}
			>
				<Animated.View
					style={[
						styles.container,
						{ backgroundColor, width: size, height: size, borderRadius: size / 2, transform: [{ scale }] },
					]}
				>
					{Ionicons ? (
						<Ionicons name={iconName as any} size={Math.round(size * 0.45)} color="white" />
					) : (
						<Text style={styles.emoji}>🎤</Text>
					)}
				</Animated.View>
			</Pressable>

		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		justifyContent: 'center',
		alignItems: 'center',
		shadowColor: '#000',
		shadowOffset: { width: 0, height: 4 },
		shadowOpacity: 0.25,
		shadowRadius: 6,
		elevation: 6,
	},
	emoji: {
		fontSize: 28,
	},
});
