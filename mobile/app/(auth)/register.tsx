import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
} from 'react-native';
import { Link } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { supabase } from '@/lib/supabase';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Text } from '@/components/ui/Text';
import { Card } from '@/components/ui/Card';
import { Colors, Spacing } from '@/constants/theme';

export default function RegisterScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleRegister() {
    setError('');
    if (!email.trim() || !password || !confirm) {
      setError('All fields are required.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    setLoading(true);
    const { error: authError } = await supabase.auth.signUp({
      email: email.trim().toLowerCase(),
      password,
    });
    setLoading(false);
    if (authError) setError(authError.message);
  }

  return (
    <SafeAreaView style={styles.safe}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={styles.kav}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.hero}>
            <Text variant="h1" style={styles.logo}>💪 GymChat</Text>
            <Text variant="body" color={Colors.textSecondary} style={styles.tagline}>
              Start tracking. Start growing.
            </Text>
          </View>

          <Card style={styles.card}>
            <Text variant="h3" style={styles.cardTitle}>Create account</Text>

            <View style={styles.fields}>
              <Input
                label="Email"
                value={email}
                onChangeText={setEmail}
                placeholder="you@example.com"
                keyboardType="email-address"
                textContentType="emailAddress"
                autoComplete="email"
              />
              <Input
                label="Password"
                value={password}
                onChangeText={setPassword}
                placeholder="At least 8 characters"
                secure
                textContentType="newPassword"
              />
              <Input
                label="Confirm password"
                value={confirm}
                onChangeText={setConfirm}
                placeholder="Repeat your password"
                secure
                textContentType="newPassword"
                onSubmitEditing={handleRegister}
              />
            </View>

            {error ? (
              <Text variant="bodySmall" color={Colors.error} style={styles.error}>
                {error}
              </Text>
            ) : null}

            <Button
              label="Create account"
              onPress={handleRegister}
              loading={loading}
              fullWidth
              size="lg"
              style={styles.btn}
            />
          </Card>

          <View style={styles.footer}>
            <Text variant="body" color={Colors.textSecondary}>Already have an account? </Text>
            <Link href="/(auth)/login" asChild>
              <TouchableOpacity>
                <Text variant="body" color={Colors.accent} weight="semibold">Sign in</Text>
              </TouchableOpacity>
            </Link>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  kav: { flex: 1 },
  scroll: { flexGrow: 1, padding: Spacing.lg, justifyContent: 'center', gap: Spacing.xl },
  hero: { alignItems: 'center', gap: Spacing.sm },
  logo: { fontSize: 32 },
  tagline: { textAlign: 'center' },
  card: { gap: Spacing.lg },
  cardTitle: { textAlign: 'center' },
  fields: { gap: Spacing.md },
  error: { textAlign: 'center' },
  btn: { marginTop: Spacing.xs },
  footer: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center' },
});
