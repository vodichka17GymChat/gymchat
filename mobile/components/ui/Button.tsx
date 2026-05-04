import React from 'react';
import {
  TouchableOpacity,
  ActivityIndicator,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { Colors, Radius, Spacing, FontSize, FontWeight } from '@/constants/theme';
import { Text } from './Text';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

interface Props {
  label: string;
  onPress: () => void;
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  style?: ViewStyle;
}

export function Button({
  label,
  onPress,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  style,
}: Props) {
  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.75}
      style={[
        styles.base,
        styles[variant],
        styles[size],
        fullWidth && styles.fullWidth,
        isDisabled && styles.disabled,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variant === 'primary' ? Colors.white : Colors.accent}
        />
      ) : (
        <Text style={[styles.label, textStyles[variant], textSizes[size]]}>
          {label}
        </Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: Radius.md,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
  // Variants
  primary: { backgroundColor: Colors.accent },
  secondary: { backgroundColor: Colors.accentLight, borderWidth: 1, borderColor: Colors.accent },
  ghost: { backgroundColor: Colors.transparent },
  danger: { backgroundColor: Colors.error },
  // Sizes
  sm: { paddingVertical: Spacing.xs, paddingHorizontal: Spacing.md, minHeight: 32 },
  md: { paddingVertical: Spacing.sm + 2, paddingHorizontal: Spacing.lg, minHeight: 44 },
  lg: { paddingVertical: Spacing.md, paddingHorizontal: Spacing.xl, minHeight: 52 },
  // States
  fullWidth: { width: '100%' },
  disabled: { opacity: 0.5 },
  label: { fontWeight: FontWeight.semibold },
});

const textStyles: Record<Variant, TextStyle> = {
  primary: { color: Colors.white },
  secondary: { color: Colors.accentStrong },
  ghost: { color: Colors.accent },
  danger: { color: Colors.white },
};

const textSizes: Record<Size, TextStyle> = {
  sm: { fontSize: FontSize.sm },
  md: { fontSize: FontSize.md },
  lg: { fontSize: FontSize.lg },
};
