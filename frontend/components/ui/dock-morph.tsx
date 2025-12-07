/**
 * DockMorph Navigation - React Native
 * 
 * Morphing dock-style navigation with glassmorphism effects
 * Adapted from web version for React Native using react-native-reanimated
 */

import React, { useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
} from 'react-native-reanimated';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { GidroAtlasColors } from '@/constants/theme';

// Alias for consistent naming throughout component
const ZamanColors = GidroAtlasColors;

const AnimatedTouchable = Animated.createAnimatedComponent(TouchableOpacity);

interface DockItem {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress?: () => void;
  badge?: number;
}

interface DockMorphProps {
  items: DockItem[];
  activeIndex?: number;
  position?: 'bottom' | 'top';
  variant?: 'default' | 'glass' | 'solid';
}

export function DockMorph({
  items,
  activeIndex = 0,
  position = 'bottom',
  variant = 'glass',
}: DockMorphProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const insets = useSafeAreaInsets();

  const getDockStyle = () => {
    if (position === 'bottom') {
      return {
        bottom: Platform.OS === 'ios' ? insets.bottom + 16 : 24,
      };
    }
    return {
      top: Platform.OS === 'ios' ? insets.top + 16 : 24,
    };
  };

  const getBackgroundStyle = () => {
    switch (variant) {
      case 'solid':
        return styles.solidBackground;
      case 'glass':
      default:
        return styles.glassBackground;
    }
  };

  return (
    <View style={[styles.container, getDockStyle()]} pointerEvents="box-none">
      <View style={[styles.dock, getBackgroundStyle()]}>
        <View style={styles.itemsContainer}>
          {items.map((item, index) => (
            <DockItem
              key={item.label}
              item={item}
              index={index}
              isActive={index === activeIndex}
              isHovered={index === hoveredIndex}
              onHoverIn={() => setHoveredIndex(index)}
              onHoverOut={() => setHoveredIndex(null)}
            />
          ))}
        </View>
      </View>
    </View>
  );
}

interface DockItemProps {
  item: DockItem;
  index: number;
  isActive: boolean;
  isHovered: boolean;
  onHoverIn: () => void;
  onHoverOut: () => void;
}

function DockItem({ item, isActive, isHovered, onHoverIn, onHoverOut }: DockItemProps) {
  const scale = useSharedValue(1);
  const bubbleScale = useSharedValue(0);
  const bubbleOpacity = useSharedValue(0);

  React.useEffect(() => {
    if (isHovered || isActive) {
      scale.value = withSpring(isActive ? 1.05 : 1.1, { damping: 12, stiffness: 200 });
      bubbleScale.value = withSpring(isActive ? 1.2 : 1.4, { damping: 15, stiffness: 180 });
      bubbleOpacity.value = withTiming(isActive ? 0.1 : 1, { duration: 200 });
    } else {
      scale.value = withSpring(1, { damping: 12, stiffness: 200 });
      bubbleScale.value = withTiming(0.6, { duration: 150 });
      bubbleOpacity.value = withTiming(0, { duration: 150 });
    }
  }, [isHovered, isActive]);

  const animatedButtonStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const animatedBubbleStyle = useAnimatedStyle(() => ({
    transform: [{ scale: bubbleScale.value }],
    opacity: bubbleOpacity.value,
  }));

  return (
    <View style={styles.itemWrapper}>
      {/* Morphic bubble background */}
      <Animated.View style={[styles.bubble, animatedBubbleStyle]} />

      {/* Icon button */}
      <AnimatedTouchable
        style={[styles.itemButton, animatedButtonStyle]}
        onPress={item.onPress}
        onPressIn={onHoverIn}
        onPressOut={onHoverOut}
        activeOpacity={0.7}
      >
        <View style={[styles.iconContainer, isActive && styles.activeIconContainer]}>
          <Ionicons
            name={item.icon}
            size={24}
            color={isActive ? GidroAtlasColors.white : GidroAtlasColors.gray[700]}
          />
        </View>
        
        {/* Badge */}
        {item.badge !== undefined && item.badge > 0 && (
          <View style={styles.badge}>
            <Text style={styles.badgeText}>
              {item.badge > 99 ? '99+' : item.badge}
            </Text>
          </View>
        )}
      </AnimatedTouchable>

      {/* Label */}
      {isHovered && (
        <Animated.View style={styles.tooltip}>
          <Text style={styles.tooltipText}>{item.label}</Text>
        </Animated.View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 100,
  },
  dock: {
    borderRadius: 32,
    paddingHorizontal: 16,
    paddingVertical: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 24,
    elevation: 8,
  },
  glassBackground: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.5)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.2,
    shadowRadius: 20,
    elevation: 10,
  },
  solidBackground: {
    backgroundColor: GidroAtlasColors.white,
    borderWidth: 1,
    borderColor: GidroAtlasColors.gray[200],
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 5,
  },
  itemsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingHorizontal: 8,
  },
  itemWrapper: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  bubble: {
    position: 'absolute',
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: `${GidroAtlasColors.persianGreen}40`,
    shadowColor: GidroAtlasColors.persianGreen,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 4,
    zIndex: 0,
  },
  itemButton: {
    position: 'relative',
    zIndex: 10,
    padding: 4,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  activeIconContainer: {
    backgroundColor: GidroAtlasColors.persianGreen,
    shadowColor: GidroAtlasColors.persianGreen,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.5,
    shadowRadius: 12,
    elevation: 8,
    transform: [{ scale: 1.1 }],
  },
  badge: {
    position: 'absolute',
    top: 2,
    right: 2,
    backgroundColor: '#FF3B30',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 6,
    borderWidth: 2,
    borderColor: GidroAtlasColors.white,
  },
  badgeText: {
    color: GidroAtlasColors.white,
    fontSize: 11,
    fontWeight: '700',
  },
  tooltip: {
    position: 'absolute',
    bottom: -40,
    backgroundColor: GidroAtlasColors.black,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    opacity: 0.9,
  },
  tooltipText: {
    color: GidroAtlasColors.white,
    fontSize: 12,
    fontWeight: '500',
  },
});

export default DockMorph;
