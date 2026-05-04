import React, { useState } from 'react';
import {
  TextInput,
  TextInputProps,
  View,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { Colors, FontSize, Radius, Spacing } from '@/constants/theme';
import { Text } from './Text';

interface Props extends TextInputProps {
  label?: string;
  error?: string;
  secure?: boolean;
}

export function Input({ label, error, secure = false, style, ...props }: Props) {
  const [hidden, setHidden] = useState(secure);

  return (
    <View style={styles.wrapper}>
      {label && <Text variant="bodySmall" weight="medium" style={styles.label}>{label}</Text>}
      <View style={[styles.inputRow, error ? styles.inputError : styles.inputNormal]}>
        <TextInput
          style={[styles.input, style]}
          placeholderTextColor={Colors.textMuted}
          secureTextEntry={hidden}
          autoCapitalize="none"
          autoCorrect={false}
          {...props}
        />
        {secure && (
          <TouchableOpacity onPress={() => setHidden(h => !h)} style={styles.eyeBtn}>
            <Text variant="caption" color={Colors.textSecondary}>{hidden ? 'Show' : 'Hide'}</Text>
          </TouchableOpacity>
        )}
      </View>
      {error && <Text variant="caption" color={Colors.error} style={styles.errorText}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: 4 },
  label: { color: Colors.textSecondary },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1.5,
    borderRadius: Radius.md,
    backgroundColor: Colors.surface,
    paddingHorizontal: Spacing.md,
    minHeight: 48,
  },
  inputNormal: { borderColor: Colors.border },
  inputError: { borderColor: Colors.error },
  input: {
    flex: 1,
    fontSize: FontSize.md,
    color: Colors.text,
    paddingVertical: Spacing.sm,
  },
  eyeBtn: { paddingLeft: Spacing.sm },
  errorText: { marginTop: 2 },
});
