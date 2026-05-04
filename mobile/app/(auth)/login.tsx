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

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleLogin() {
    if (!email.trim() || !password) {
      setError('Email and password are required.');
      return;
    }
    setError('');
    setLoading(true);
    const { error: authError } = await supabase.auth.signInWithPassword({
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
          {/* Logo / hero */}
          <View style={styles.hero}>
            <Text variant="h1" style={styles.logo}>💪 GymChat</Text>
            <Text variant="body" color={Colors.textSecondary} style={styles.tagline}>
              Track every rep. Build your best self.
            </Text>
          </View>

          <Card style={styles.card}>
            <Text variant="h3" style={styles.cardTitle}>Sign in</Text>

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
                placeholder="Your password"
                secure
                textContentType="password"
                autoComplete="password"
                onSubmitEditing={handleLogin}
              />
            </View>

            {error ? (
              <Text variant="bodySmall" color={Colors.error} style={styles.error}>
                {error}
              </Text>
            ) : null}

            <Button
              label="Sign in"
              onPress={handleLogin}
              loading={loading}
              fullWidth
              size="lg"
              style={styles.btn}
            />
          </Card>

          <View style={styles.footer}>
            <Text variant="body" color={Colors.textSecondary}>Don't have an account? </Text>
            <Link href="/(auth)/register" asChild>
              <TouchableOpacity>
                <Text variant="body" color={Colors.accent} weight="semibold">Create one</Text>
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
