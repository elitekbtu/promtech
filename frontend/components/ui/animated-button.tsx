/**
 * Animated Button Component for React Native
 * 
 * Beautiful animated buttons with entrance animations similar to framer-motion
 */

import React, { useEffect } from 'react';
import { TouchableOpacity, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withDelay,
  withTiming,
  Easing,
  interpolate,
} from 'react-native-reanimated';
import { Ionicons } from '@expo/vector-icons';

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

interface AnimatedButtonProps {
  title: string;
  onPress: () => void;
  icon?: keyof typeof Ionicons.glyphMap;
  iconColor?: string;
  variant?: 'default' | 'dark' | 'outline' | 'solar';
  delay?: number;
  disabled?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export function AnimatedButton({
  title,
  onPress,
  icon,
  iconColor,
  variant = 'default',
  delay = 0,
  disabled = false,
  style,
  textStyle,
}: AnimatedButtonProps) {
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(40);
  const scale = useSharedValue(0.95);

  useEffect(() => {
    opacity.value = withDelay(
      delay,
      withTiming(1, { duration: 600, easing: Easing.out(Easing.cubic) })
    );
    translateY.value = withDelay(
      delay,
      withSpring(0, { damping: 15, stiffness: 100 })
    );
    scale.value = withDelay(
      delay,
      withSpring(1, { damping: 12, stiffness: 100 })
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [
      { translateY: translateY.value },
      { scale: scale.value },
    ],
  }));

  const getButtonStyle = () => {
    switch (variant) {
      case 'dark':
        return styles.darkButton;
      case 'outline':
        return styles.outlineButton;
      case 'solar':
        return styles.solarButton;
      default:
        return styles.defaultButton;
    }
  };

  const getTextStyle = () => {
    switch (variant) {
      case 'dark':
        return styles.darkButtonText;
      case 'outline':
        return styles.outlineButtonText;
      case 'solar':
        return styles.solarButtonText;
      default:
        return styles.defaultButtonText;
    }
  };

  const getIconColor = () => {
    if (iconColor) return iconColor;
    switch (variant) {
      case 'dark':
        return '#FFFFFF';
      case 'outline':
        return '#1A1A1A';
      case 'solar':
        return '#1A1A1A';
      default:
        return '#1A1A1A';
    }
  };

  return (
    <AnimatedTouchable
      style={[styles.button, getButtonStyle(), animatedStyle, style]}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.8}
    >
      {icon && (
        <Ionicons name={icon} size={24} color={getIconColor()} style={styles.icon} />
      )}
      <Text style={[styles.buttonText, getTextStyle(), textStyle]}>{title}</Text>
    </AnimatedTouchable>
  );
}

/**
 * Animated Text Component
 */
interface AnimatedTextProps {
  children: React.ReactNode;
  delay?: number;
  style?: TextStyle;
  variant?: 'title' | 'subtitle' | 'body';
}

export function AnimatedText({
  children,
  delay = 0,
  style,
  variant = 'body',
}: AnimatedTextProps) {
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(30);

  useEffect(() => {
    opacity.value = withDelay(
      delay,
      withTiming(1, { duration: 800, easing: Easing.out(Easing.cubic) })
    );
    translateY.value = withDelay(
      delay,
      withSpring(0, { damping: 15, stiffness: 80 })
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: translateY.value }],
  }));

  const getTextStyle = () => {
    switch (variant) {
      case 'title':
        return styles.titleText;
      case 'subtitle':
        return styles.subtitleText;
      default:
        return styles.bodyText;
    }
  };

  return (
    <Animated.Text style={[getTextStyle(), animatedStyle, style]}>
      {children}
    </Animated.Text>
  );
}

/**
 * Animated View Component
 */
interface AnimatedContainerProps {
  children: React.ReactNode;
  delay?: number;
  style?: ViewStyle;
}

export function AnimatedContainer({
  children,
  delay = 0,
  style,
}: AnimatedContainerProps) {
  const opacity = useSharedValue(0);
  const translateY = useSharedValue(40);

  useEffect(() => {
    opacity.value = withDelay(
      delay,
      withTiming(1, { duration: 800, easing: Easing.out(Easing.cubic) })
    );
    translateY.value = withDelay(
      delay,
      withSpring(0, { damping: 15, stiffness: 80 })
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
    transform: [{ translateY: translateY.value }],
  }));

  return (
    <Animated.View style={[animatedStyle, style]}>
      {children}
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 18,
    paddingHorizontal: 32,
    borderRadius: 50, // Fully rounded like the demo
    marginVertical: 8,
    gap: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 12,
    elevation: 5,
  },
  defaultButton: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  darkButton: {
    backgroundColor: '#1A1A1A',
    borderWidth: 0,
  },
  outlineButton: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#1A1A1A',
  },
  solarButton: {
    backgroundColor: '#EEFE6D',
    borderWidth: 0,
  },
  buttonText: {
    fontSize: 17,
    fontWeight: '600',
    letterSpacing: 0.3,
  },
  defaultButtonText: {
    color: '#1A1A1A',
  },
  darkButtonText: {
    color: '#FFFFFF',
  },
  outlineButtonText: {
    color: '#1A1A1A',
  },
  solarButtonText: {
    color: '#1A1A1A',
  },
  icon: {
    marginRight: 4,
  },
  titleText: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1A1A1A',
    textAlign: 'center',
  },
  subtitleText: {
    fontSize: 18,
    fontWeight: '300',
    color: '#6B7280',
    textAlign: 'center',
  },
  bodyText: {
    fontSize: 16,
    color: '#374151',
    textAlign: 'center',
  },
});

export default AnimatedButton;
