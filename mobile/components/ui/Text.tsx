import React from 'react';
import { Text as RNText, TextProps, StyleSheet } from 'react-native';
import { Colors, FontSize, FontWeight } from '@/constants/theme';

type Variant = 'h1' | 'h2' | 'h3' | 'body' | 'bodySmall' | 'label' | 'caption';

interface Props extends TextProps {
  variant?: Variant;
  color?: string;
  weight?: keyof typeof FontWeight;
}

export function Text({ variant = 'body', color, weight, style, ...props }: Props) {
  return (
    <RNText
      style={[
        styles[variant],
        color ? { color } : undefined,
        weight ? { fontWeight: FontWeight[weight] } : undefined,
        style,
      ]}
      {...props}
    />
  );
}

const styles = StyleSheet.create({
  h1: { fontSize: FontSize['3xl'], fontWeight: FontWeight.bold, color: Colors.text, lineHeight: 36 },
  h2: { fontSize: FontSize['2xl'], fontWeight: FontWeight.bold, color: Colors.text, lineHeight: 30 },
  h3: { fontSize: FontSize.xl, fontWeight: FontWeight.semibold, color: Colors.text, lineHeight: 26 },
  body: { fontSize: FontSize.md, fontWeight: FontWeight.regular, color: Colors.text, lineHeight: 22 },
  bodySmall: { fontSize: FontSize.sm, fontWeight: FontWeight.regular, color: Colors.text, lineHeight: 19 },
  label: { fontSize: FontSize.sm, fontWeight: FontWeight.semibold, color: Colors.textSecondary, lineHeight: 18, textTransform: 'uppercase', letterSpacing: 0.5 },
  caption: { fontSize: FontSize.xs, fontWeight: FontWeight.regular, color: Colors.textMuted, lineHeight: 16 },
});
