/**
 * Aurora Background Component for React Native
 * 
 * Beautiful animated gradient background with aurora-like effects
 * Adapted from the web version for React Native using expo-linear-gradient and reanimated
 */

import React, { useEffect, ReactNode } from 'react';
import { View, StyleSheet, Dimensions, Platform } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  Easing,
  interpolate,
} from 'react-native-reanimated';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface AuroraBackgroundProps {
  children: ReactNode;
  /** Primary aurora color */
  primaryColor?: string;
  /** Secondary aurora color */
  secondaryColor?: string;
  /** Accent color for highlights */
  accentColor?: string;
  /** Background color */
  backgroundColor?: string;
  /** Animation duration in ms */
  animationDuration?: number;
  /** Show radial gradient mask */
  showRadialGradient?: boolean;
  /** Intensity of the aurora effect (0-1) */
  intensity?: number;
}

const AnimatedLinearGradient = Animated.createAnimatedComponent(LinearGradient);

export function AuroraBackground({
  children,
  primaryColor = '#2D9A86',    // Persian Green
  secondaryColor = '#4FD1C5',  // Teal
  accentColor = '#EEFE6D',     // Solar Yellow
  backgroundColor = '#F5F9F8', // Cloud
  animationDuration = 8000,
  showRadialGradient = true,
  intensity = 0.6,
}: AuroraBackgroundProps) {
  // Animation values
  const progress1 = useSharedValue(0);
  const progress2 = useSharedValue(0);
  const progress3 = useSharedValue(0);

  useEffect(() => {
    // Start animations with different speeds for organic feel
    progress1.value = withRepeat(
      withTiming(1, { duration: animationDuration, easing: Easing.linear }),
      -1,
      true
    );
    progress2.value = withRepeat(
      withTiming(1, { duration: animationDuration * 1.3, easing: Easing.linear }),
      -1,
      true
    );
    progress3.value = withRepeat(
      withTiming(1, { duration: animationDuration * 0.7, easing: Easing.linear }),
      -1,
      true
    );
  }, [animationDuration]);

  // Animated styles for each aurora layer
  const auroraStyle1 = useAnimatedStyle(() => {
    const translateX = interpolate(progress1.value, [0, 1], [-100, 100]);
    const translateY = interpolate(progress1.value, [0, 1], [-50, 50]);
    const scale = interpolate(progress1.value, [0, 0.5, 1], [1, 1.2, 1]);
    
    return {
      transform: [
        { translateX },
        { translateY },
        { scale },
        { rotate: `${interpolate(progress1.value, [0, 1], [0, 15])}deg` },
      ],
      opacity: intensity * 0.7,
    };
  });

  const auroraStyle2 = useAnimatedStyle(() => {
    const translateX = interpolate(progress2.value, [0, 1], [80, -80]);
    const translateY = interpolate(progress2.value, [0, 1], [30, -30]);
    const scale = interpolate(progress2.value, [0, 0.5, 1], [1.1, 0.9, 1.1]);
    
    return {
      transform: [
        { translateX },
        { translateY },
        { scale },
        { rotate: `${interpolate(progress2.value, [0, 1], [-10, 10])}deg` },
      ],
      opacity: intensity * 0.5,
    };
  });

  const auroraStyle3 = useAnimatedStyle(() => {
    const translateX = interpolate(progress3.value, [0, 1], [-60, 60]);
    const translateY = interpolate(progress3.value, [0, 1], [-80, 80]);
    const scale = interpolate(progress3.value, [0, 0.5, 1], [0.9, 1.3, 0.9]);
    
    return {
      transform: [
        { translateX },
        { translateY },
        { scale },
        { rotate: `${interpolate(progress3.value, [0, 1], [5, -5])}deg` },
      ],
      opacity: intensity * 0.4,
    };
  });

  return (
    <View style={[styles.container, { backgroundColor }]}>
      {/* Aurora Layer 1 - Primary */}
      <Animated.View style={[styles.auroraLayer, styles.layer1, auroraStyle1]}>
        <LinearGradient
          colors={[
            `${primaryColor}00`,
            `${primaryColor}40`,
            `${primaryColor}60`,
            `${primaryColor}40`,
            `${primaryColor}00`,
          ]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={styles.gradient}
        />
      </Animated.View>

      {/* Aurora Layer 2 - Secondary */}
      <Animated.View style={[styles.auroraLayer, styles.layer2, auroraStyle2]}>
        <LinearGradient
          colors={[
            `${secondaryColor}00`,
            `${secondaryColor}30`,
            `${secondaryColor}50`,
            `${secondaryColor}30`,
            `${secondaryColor}00`,
          ]}
          start={{ x: 0.2, y: 0 }}
          end={{ x: 0.8, y: 1 }}
          style={styles.gradient}
        />
      </Animated.View>

      {/* Aurora Layer 3 - Accent */}
      <Animated.View style={[styles.auroraLayer, styles.layer3, auroraStyle3]}>
        <LinearGradient
          colors={[
            `${accentColor}00`,
            `${accentColor}20`,
            `${accentColor}35`,
            `${accentColor}20`,
            `${accentColor}00`,
          ]}
          start={{ x: 0.5, y: 0 }}
          end={{ x: 0.5, y: 1 }}
          style={styles.gradient}
        />
      </Animated.View>

      {/* Radial gradient overlay for depth */}
      {showRadialGradient && (
        <View style={styles.radialOverlay}>
          <LinearGradient
            colors={[
              `${backgroundColor}00`,
              `${backgroundColor}40`,
              `${backgroundColor}90`,
            ]}
            start={{ x: 0.5, y: 0 }}
            end={{ x: 0.5, y: 1 }}
            style={styles.gradient}
          />
        </View>
      )}

      {/* Content */}
      <View style={styles.content}>
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    overflow: 'hidden',
  },
  auroraLayer: {
    position: 'absolute',
    overflow: 'hidden',
  },
  layer1: {
    top: -SCREEN_HEIGHT * 0.3,
    left: -SCREEN_WIDTH * 0.2,
    width: SCREEN_WIDTH * 1.5,
    height: SCREEN_HEIGHT * 0.8,
    borderRadius: SCREEN_WIDTH,
  },
  layer2: {
    top: SCREEN_HEIGHT * 0.1,
    right: -SCREEN_WIDTH * 0.3,
    width: SCREEN_WIDTH * 1.2,
    height: SCREEN_HEIGHT * 0.6,
    borderRadius: SCREEN_WIDTH * 0.8,
  },
  layer3: {
    bottom: -SCREEN_HEIGHT * 0.2,
    left: -SCREEN_WIDTH * 0.1,
    width: SCREEN_WIDTH * 1.3,
    height: SCREEN_HEIGHT * 0.5,
    borderRadius: SCREEN_WIDTH * 0.6,
  },
  gradient: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  radialOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: SCREEN_HEIGHT * 0.4,
  },
  content: {
    flex: 1,
    zIndex: 10,
  },
});

export default AuroraBackground;
