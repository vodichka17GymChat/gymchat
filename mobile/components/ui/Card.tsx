import React from 'react';
import { View, ViewProps, StyleSheet } from 'react-native';
import { Colors, Radius, Shadow, Spacing } from '@/constants/theme';

interface Props extends ViewProps {
  padded?: boolean;
}

export function Card({ padded = true, style, children, ...props }: Props) {
  return (
    <View style={[styles.card, padded && styles.padded, style]} {...props}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.lg,
    borderWidth: 1,
    borderColor: Colors.border,
    ...Shadow.sm,
  },
  padded: {
    padding: Spacing.lg,
  },
});
