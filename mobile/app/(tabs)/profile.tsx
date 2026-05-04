import React, { useState, useCallback } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { supabase } from '@/lib/supabase';
import { Text } from '@/components/ui/Text';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Colors, Spacing } from '@/constants/theme';
import { ATHLETE_TYPES, PRIMARY_GOALS, FITNESS_LEVELS } from '@/constants/config';

// Simple segmented picker using TouchableOpacity buttons
function OptionPicker({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: readonly string[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <View style={styles.pickerWrapper}>
      <Text variant="bodySmall" weight="medium" color={Colors.textSecondary} style={styles.pickerLabel}>
        {label}
      </Text>
      <View style={styles.pickerRow}>
        {options.map(opt => (
          <Button
            key={opt}
            label={opt}
            onPress={() => onChange(opt)}
            variant={value === opt ? 'primary' : 'secondary'}
            size="sm"
            style={styles.pickerBtn}
          />
        ))}
      </View>
    </View>
  );
}

export default function ProfileScreen() {
  const [email, setEmail] = useState('');
  const [age, setAge] = useState('');
  const [heightCm, setHeightCm] = useState('');
  const [weightKg, setWeightKg] = useState('');
  const [fitnessLevel, setFitnessLevel] = useState('');
  const [athleteType, setAthleteType] = useState('');
  const [primaryGoal, setPrimaryGoal] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  async function loadProfile() {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;
    setEmail(user.email ?? '');

    const { data } = await supabase
      .from('users')
      .select('*')
      .eq('user_id', user.id)
      .single();

    if (data) {
      setAge(data.age ? String(data.age) : '');
      setHeightCm(data.height_cm ? String(data.height_cm) : '');
      setWeightKg(data.weight_kg ? String(data.weight_kg) : '');
      setFitnessLevel(data.fitness_level ?? '');
      setAthleteType(data.athlete_type ?? '');
      setPrimaryGoal(data.primary_goal ?? '');
    }
  }

  useFocusEffect(useCallback(() => { loadProfile(); }, []));

  async function handleSave() {
    setError('');
    setSaving(true);

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const updates = {
      age: age ? parseInt(age) : null,
      height_cm: heightCm ? parseFloat(heightCm) : null,
      weight_kg: weightKg ? parseFloat(weightKg) : null,
      fitness_level: fitnessLevel || null,
      athlete_type: athleteType || null,
      primary_goal: primaryGoal || null,
      updated_at: new Date().toISOString(),
    };

    const { error: saveError } = await supabase
      .from('users')
      .update(updates)
      .eq('user_id', user.id);

    setSaving(false);
    if (saveError) {
      setError(saveError.message);
    } else {
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  }

  async function handleSignOut() {
    await supabase.auth.signOut();
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text variant="h2" style={styles.title}>Profile</Text>

        <Card style={styles.accountCard}>
          <Text variant="bodySmall" color={Colors.textSecondary}>{email}</Text>
          <Button label="Sign out" onPress={handleSignOut} variant="ghost" size="sm" />
        </Card>

        <Text variant="label" style={styles.sectionLabel}>Body metrics</Text>
        <Card style={styles.section}>
          <View style={styles.row}>
            <View style={styles.half}>
              <Input label="Age" value={age} onChangeText={setAge} keyboardType="number-pad" placeholder="25" />
            </View>
            <View style={styles.half}>
              <Input label="Height (cm)" value={heightCm} onChangeText={setHeightCm} keyboardType="decimal-pad" placeholder="175" />
            </View>
          </View>
          <Input label="Weight (kg)" value={weightKg} onChangeText={setWeightKg} keyboardType="decimal-pad" placeholder="75" />
        </Card>

        <Text variant="label" style={styles.sectionLabel}>Training profile</Text>
        <Card style={styles.section}>
          <OptionPicker label="Fitness level" options={FITNESS_LEVELS} value={fitnessLevel} onChange={setFitnessLevel} />
          <OptionPicker label="Athlete type" options={ATHLETE_TYPES} value={athleteType} onChange={setAthleteType} />
          <OptionPicker label="Primary goal" options={PRIMARY_GOALS} value={primaryGoal} onChange={setPrimaryGoal} />
        </Card>

        {error ? <Text variant="bodySmall" color={Colors.error}>{error}</Text> : null}

        <Button
          label={saved ? '✓ Saved' : 'Save changes'}
          onPress={handleSave}
          loading={saving}
          fullWidth
          size="lg"
          style={styles.saveBtn}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { padding: Spacing.lg, gap: Spacing.md },
  title: { marginBottom: Spacing.xs },
  accountCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  sectionLabel: { marginTop: Spacing.xs },
  section: { gap: Spacing.md },
  row: { flexDirection: 'row', gap: Spacing.sm },
  half: { flex: 1 },
  pickerWrapper: { gap: Spacing.xs },
  pickerLabel: {},
  pickerRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs },
  pickerBtn: { marginBottom: 0 },
  saveBtn: { marginTop: Spacing.sm },
});
