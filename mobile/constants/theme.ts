/**
 * Design tokens — mirrors the CSS custom properties in the Streamlit
 * prototype's components/theme.py. Sky/cyan accent, clean white surfaces.
 */

export const Colors = {
  // Backgrounds
  bg: '#F0F4F8',
  surface: '#FFFFFF',
  surfaceElevated: '#FFFFFF',

  // Accent
  accent: '#0EA5E9',         // sky-500
  accentStrong: '#0284C7',   // sky-600
  accentLight: '#E0F2FE',    // sky-100

  // Text
  text: '#1B2A41',
  textSecondary: '#6B7A90',
  textMuted: '#9BACCB',
  textOnAccent: '#FFFFFF',

  // Borders & dividers
  border: '#E2E8F0',
  divider: '#F1F5F9',

  // Status
  success: '#10B981',
  successLight: '#D1FAE5',
  warning: '#F59E0B',
  warningLight: '#FEF3C7',
  error: '#EF4444',
  errorLight: '#FEE2E2',

  // Neutral
  white: '#FFFFFF',
  black: '#000000',
  transparent: 'transparent',
} as const;

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  '2xl': 24,
  '3xl': 32,
  '4xl': 40,
  '5xl': 48,
} as const;

export const Radius = {
  sm: 6,
  md: 10,
  lg: 14,
  xl: 18,
  full: 999,
} as const;

export const FontSize = {
  xs: 11,
  sm: 13,
  md: 15,
  lg: 17,
  xl: 20,
  '2xl': 24,
  '3xl': 28,
  '4xl': 32,
} as const;

export const FontWeight = {
  regular: '400' as const,
  medium: '500' as const,
  semibold: '600' as const,
  bold: '700' as const,
};

export const Shadow = {
  sm: {
    shadowColor: '#1B2A41',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  md: {
    shadowColor: '#1B2A41',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 4,
  },
} as const;
