/**
 * GidroAtlas Color DNA
 */

import { Platform } from 'react-native';

// GidroAtlas Brand Colors
export const GidroAtlasColors = {
  persianGreen: '#2D9A86',
  solar: '#EEFE6D',
  cloud: '#F5F9F8',
  white: '#FFFFFF',
  black: '#1A1A1A',
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
};

const tintColorLight = GidroAtlasColors.persianGreen;
const tintColorDark = GidroAtlasColors.solar;

export const Colors = {
  light: {
    text: GidroAtlasColors.black,
    background: GidroAtlasColors.white,
    backgroundSecondary: GidroAtlasColors.cloud,
    tint: tintColorLight,
    primary: GidroAtlasColors.persianGreen,
    accent: GidroAtlasColors.solar,
    icon: GidroAtlasColors.gray[600],
    tabIconDefault: GidroAtlasColors.gray[400],
    tabIconSelected: tintColorLight,
    border: GidroAtlasColors.gray[200],
  },
  dark: {
    text: GidroAtlasColors.cloud,
    background: GidroAtlasColors.gray[900],
    backgroundSecondary: GidroAtlasColors.gray[800],
    tint: tintColorDark,
    primary: GidroAtlasColors.persianGreen,
    accent: GidroAtlasColors.solar,
    icon: GidroAtlasColors.gray[400],
    tabIconDefault: GidroAtlasColors.gray[500],
    tabIconSelected: tintColorDark,
    border: GidroAtlasColors.gray[700],
  },
};

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },
});
