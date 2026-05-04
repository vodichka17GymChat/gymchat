import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
} from 'react-native';
import { useFocusEffect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { supabase } from '@/lib/supabase';
import { Text } from '@/components/ui/Text';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Colors, Spacing, Radius, FontSize } from '@/constants/theme';
import { WORKOUT_TYPES } from '@/constants/config';
import type { WorkoutSessionRow, ExecutionWithExercise, SetRow } from '@/lib/types';

// ── Types ─────────────────────────────────────────────────────────────────

interface Exercise {
  exercise_id: number;
  exercise_name: string;
  muscle_group: string;
}

// ── Exercise Picker ───────────────────────────────────────────────────────

function ExercisePicker({
  onSelect,
  onCancel,
}: {
  onSelect: (ex: Exercise) => void;
  onCancel: () => void;
}) {
  const [search, setSearch] = useState('');
  const [exercises, setExercises] = useState<Exercise[]>([]);

  async function doSearch(q: string) {
    setSearch(q);
    let query = supabase
      .from('exercises')
      .select('exercise_id, exercise_name, muscle_group')
      .order('exercise_name')
      .limit(40);

    if (q.trim()) {
      query = query.ilike('exercise_name', `%${q.trim()}%`);
    }

    const { data } = await query;
    setExercises(data ?? []);
  }

  useEffect(() => { doSearch(''); }, []);

  return (
    <Card style={styles.picker}>
      <View style={styles.pickerHeader}>
        <Text variant="h3">Add exercise</Text>
        <TouchableOpacity onPress={onCancel}>
          <Text variant="body" color={Colors.textSecondary}>Cancel</Text>
        </TouchableOpacity>
      </View>
      <Input
        placeholder="Search exercises..."
        value={search}
        onChangeText={doSearch}
        autoFocus
      />
      <ScrollView style={styles.pickerList} nestedScrollEnabled>
        {exercises.map(ex => (
          <TouchableOpacity
            key={ex.exercise_id}
            style={styles.exerciseOption}
            onPress={() => onSelect(ex)}
          >
            <Text variant="body" weight="medium">{ex.exercise_name}</Text>
            <Text variant="caption" color={Colors.textMuted}>{ex.muscle_group}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </Card>
  );
}

// ── Set Row ───────────────────────────────────────────────────────────────

function SetRowItem({ set, onDelete }: { set: SetRow; onDelete: () => void }) {
  return (
    <View style={styles.setRow}>
      <Text variant="caption" color={Colors.textMuted} style={styles.setNum}>
        {set.set_number}
      </Text>
      <Text variant="bodySmall" style={styles.setMain}>
        {set.weight_kg} kg × {set.reps}
      </Text>
      {set.rpe != null && (
        <Text variant="caption" color={Colors.textMuted}>RPE {set.rpe}</Text>
      )}
      <TouchableOpacity onPress={onDelete} style={styles.deleteBtn}>
        <Text variant="caption" color={Colors.error}>✕</Text>
      </TouchableOpacity>
    </View>
  );
}

// ── Set Logger Form ───────────────────────────────────────────────────────

function SetLoggerForm({
  executionId,
  defaultWeight,
  defaultReps,
  onLogged,
}: {
  executionId: number;
  defaultWeight: number;
  defaultReps: number;
  onLogged: () => void;
}) {
  const [weight, setWeight] = useState(defaultWeight > 0 ? String(defaultWeight) : '');
  const [reps, setReps] = useState(defaultReps > 0 ? String(defaultReps) : '');
  const [rpe, setRpe] = useState('');
  const [logging, setLogging] = useState(false);

  async function handleLog() {
    const w = parseFloat(weight);
    const r = parseInt(reps);
    if (isNaN(w) || isNaN(r) || r < 1) return;

    setLogging(true);

    const { data: existing } = await supabase
      .from('sets')
      .select('set_number')
      .eq('execution_id', executionId)
      .order('set_number', { ascending: false })
      .limit(1);

    const nextSetNumber = (existing?.[0]?.set_number ?? 0) + 1;

    await supabase.from('sets').insert({
      execution_id: executionId,
      set_number: nextSetNumber,
      timestamp: new Date().toISOString(),
      weight_kg: w,
      reps: r,
      rpe: rpe ? parseInt(rpe) : null,
      rir: null,
      rest_seconds: null,
    });

    setLogging(false);
    onLogged();
  }

  return (
    <View style={styles.logForm}>
      <View style={styles.logRow}>
        <View style={styles.logField}>
          <Text variant="caption" color={Colors.textSecondary}>Weight (kg)</Text>
          <TextInput
            style={styles.logInput}
            value={weight}
            onChangeText={setWeight}
            keyboardType="decimal-pad"
            placeholder="0"
            placeholderTextColor={Colors.textMuted}
          />
        </View>
        <View style={styles.logField}>
          <Text variant="caption" color={Colors.textSecondary}>Reps</Text>
          <TextInput
            style={styles.logInput}
            value={reps}
            onChangeText={setReps}
            keyboardType="number-pad"
            placeholder="0"
            placeholderTextColor={Colors.textMuted}
          />
        </View>
        <View style={[styles.logField, styles.logFieldSm]}>
          <Text variant="caption" color={Colors.textSecondary}>RPE</Text>
          <TextInput
            style={styles.logInput}
            value={rpe}
            onChangeText={setRpe}
            keyboardType="number-pad"
            placeholder="—"
            placeholderTextColor={Colors.textMuted}
          />
        </View>
        <Button
          label="Log"
          onPress={handleLog}
          loading={logging}
          size="sm"
          style={styles.logBtn}
        />
      </View>
    </View>
  );
}

// ── Exercise Card ─────────────────────────────────────────────────────────

function ExerciseCard({
  execution,
  defaultExpanded,
}: {
  execution: ExecutionWithExercise;
  defaultExpanded: boolean;
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [sets, setSets] = useState<SetRow[]>([]);

  async function loadSets() {
    const { data } = await supabase
      .from('sets')
      .select('*')
      .eq('execution_id', execution.execution_id)
      .order('set_number');
    setSets(data ?? []);
  }

  useEffect(() => { loadSets(); }, [execution.execution_id]);

  async function deleteSet(setId: number) {
    await supabase.from('sets').delete().eq('set_id', setId);
    loadSets();
  }

  // Pre-fill from the most recently logged set in this execution
  const lastSet = sets[sets.length - 1];
  const defaultWeight = lastSet?.weight_kg ?? 0;
  const defaultReps = lastSet?.reps ?? 0;

  return (
    <Card style={expanded ? styles.exerciseCardExpanded : undefined}>
      <TouchableOpacity
        onPress={() => setExpanded(e => !e)}
        style={styles.exerciseCardHeader}
      >
        <View>
          <Text variant="body" weight="semibold">{execution.exercise_name}</Text>
          <Text variant="caption" color={Colors.textMuted}>
            {execution.muscle_group} · {sets.length} set{sets.length !== 1 ? 's' : ''}
          </Text>
        </View>
        <Text variant="caption" color={Colors.textMuted}>{expanded ? '▲' : '▼'}</Text>
      </TouchableOpacity>

      {expanded && (
        <View style={styles.exerciseCardBody}>
          {sets.map(s => (
            <SetRowItem key={s.set_id} set={s} onDelete={() => deleteSet(s.set_id)} />
          ))}
          <SetLoggerForm
            executionId={execution.execution_id}
            defaultWeight={defaultWeight}
            defaultReps={defaultReps}
            onLogged={loadSets}
          />
        </View>
      )}
    </Card>
  );
}

// ── Start Form ────────────────────────────────────────────────────────────

function StartForm({ onStart }: { onStart: () => void }) {
  const [workoutType, setWorkoutType] = useState(WORKOUT_TYPES[0]);
  const [starting, setStarting] = useState(false);

  async function handleStart() {
    setStarting(true);
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) { setStarting(false); return; }

    await supabase.from('workout_sessions').insert({
      user_id: user.id,
      workout_type: workoutType,
      start_time: new Date().toISOString(),
    });

    setStarting(false);
    onStart();
  }

  return (
    <Card style={styles.startForm}>
      <Text variant="h3">Start a workout</Text>
      <View style={styles.typeRow}>
        {WORKOUT_TYPES.map(t => (
          <TouchableOpacity
            key={t}
            style={[styles.typeChip, workoutType === t && styles.typeChipActive]}
            onPress={() => setWorkoutType(t)}
          >
            <Text
              variant="bodySmall"
              weight={workoutType === t ? 'semibold' : 'regular'}
              color={workoutType === t ? Colors.white : Colors.textSecondary}
            >
              {t}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <Button label="Begin workout" onPress={handleStart} loading={starting} fullWidth size="lg" />
    </Card>
  );
}

// ── Main Screen ───────────────────────────────────────────────────────────

export default function WorkoutScreen() {
  const [session, setSession] = useState<WorkoutSessionRow | null>(null);
  const [executions, setExecutions] = useState<ExecutionWithExercise[]>([]);
  const [showPicker, setShowPicker] = useState(false);
  const [showEndForm, setShowEndForm] = useState(false);
  const [notes, setNotes] = useState('');
  const [lastExecutionId, setLastExecutionId] = useState<number | null>(null);

  async function loadSession() {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const { data } = await supabase
      .from('workout_sessions')
      .select('*')
      .eq('user_id', user.id)
      .is('end_time', null)
      .order('start_time', { ascending: false })
      .limit(1)
      .maybeSingle();

    setSession(data ?? null);
    if (data) loadExecutions(data.session_id);
    else setExecutions([]);
  }

  async function loadExecutions(sessionId: number) {
    const { data } = await supabase
      .from('exercise_executions')
      .select('*, exercises(exercise_name, muscle_group, exercise_type)')
      .eq('session_id', sessionId)
      .order('execution_order');

    const enriched: ExecutionWithExercise[] = (data ?? []).map(ex => ({
      ...ex,
      exercise_name: (ex.exercises as { exercise_name: string }).exercise_name,
      muscle_group: (ex.exercises as { muscle_group: string }).muscle_group,
      exercise_type: (ex.exercises as { exercise_type: string }).exercise_type as 'compound' | 'isolation',
    }));

    setExecutions(enriched);
  }

  useFocusEffect(useCallback(() => { loadSession(); }, []));

  async function addExercise(ex: Exercise) {
    if (!session) return;
    setShowPicker(false);

    const { data } = await supabase
      .from('exercise_executions')
      .insert({
        session_id: session.session_id,
        exercise_id: ex.exercise_id,
        execution_order: executions.length + 1,
      })
      .select('execution_id')
      .single();

    if (data) setLastExecutionId(data.execution_id);
    loadExecutions(session.session_id);
  }

  async function endSession() {
    if (!session) return;
    await supabase
      .from('workout_sessions')
      .update({ end_time: new Date().toISOString(), notes: notes || null })
      .eq('session_id', session.session_id);

    setSession(null);
    setExecutions([]);
    setShowEndForm(false);
    setNotes('');
    setLastExecutionId(null);
  }

  // ── No active session ─────────────────────────────────────────
  if (!session) {
    return (
      <SafeAreaView style={styles.safe}>
        <ScrollView contentContainerStyle={styles.scroll}>
          <Text variant="h2" style={styles.title}>Workout</Text>
          <StartForm onStart={loadSession} />
        </ScrollView>
      </SafeAreaView>
    );
  }

  // ── Active session ────────────────────────────────────────────
  const elapsed = Math.floor((Date.now() - new Date(session.start_time).getTime()) / 60000);
  const focusedId = lastExecutionId ?? executions[executions.length - 1]?.execution_id ?? null;

  return (
    <SafeAreaView style={styles.safe}>
      {showPicker && (
        <View style={styles.pickerOverlay}>
          <ExercisePicker onSelect={addExercise} onCancel={() => setShowPicker(false)} />
        </View>
      )}

      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Session header */}
        <Card style={styles.sessionHeaderCard}>
          <View style={styles.sessionInfo}>
            <View style={styles.activeDotRow}>
              <View style={styles.activeDot} />
              <Text variant="body" weight="semibold">{session.workout_type ?? 'Workout'}</Text>
            </View>
            <Text variant="caption" color={Colors.textMuted}>
              {elapsed}m elapsed · {executions.length} exercise{executions.length !== 1 ? 's' : ''}
            </Text>
          </View>
          <Button label="End" onPress={() => setShowEndForm(true)} variant="secondary" size="sm" />
        </Card>

        {/* End form */}
        {showEndForm && (
          <Card style={styles.endForm}>
            <Text variant="body" weight="semibold">End workout?</Text>
            <Input
              label="Notes (optional)"
              value={notes}
              onChangeText={setNotes}
              placeholder="How did it go?"
              multiline
            />
            <View style={styles.endBtns}>
              <Button label="Cancel" onPress={() => setShowEndForm(false)} variant="ghost" style={styles.endBtn} />
              <Button label="Confirm" onPress={endSession} style={styles.endBtn} />
            </View>
          </Card>
        )}

        {/* Exercise cards — newest first */}
        {executions.length === 0 ? (
          <Card>
            <Text variant="body" color={Colors.textSecondary}>
              No exercises yet. Add your first one below.
            </Text>
          </Card>
        ) : (
          [...executions].reverse().map(ex => (
            <ExerciseCard
              key={ex.execution_id}
              execution={ex}
              defaultExpanded={ex.execution_id === focusedId}
            />
          ))
        )}

        <Button
          label="+ Add exercise"
          onPress={() => setShowPicker(true)}
          variant="secondary"
          fullWidth
        />
      </ScrollView>
    </SafeAreaView>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { padding: Spacing.lg, gap: Spacing.sm },
  title: { marginBottom: Spacing.xs },

  startForm: { gap: Spacing.md },
  typeRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs },
  typeChip: {
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.xs,
    borderRadius: Radius.full,
    backgroundColor: Colors.accentLight,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  typeChipActive: { backgroundColor: Colors.accent, borderColor: Colors.accent },

  sessionHeaderCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  sessionInfo: { gap: 2 },
  activeDotRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.xs },
  activeDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: Colors.success },

  endForm: { gap: Spacing.md, borderColor: Colors.warning },
  endBtns: { flexDirection: 'row', gap: Spacing.sm },
  endBtn: { flex: 1 },

  exerciseCardExpanded: { borderColor: Colors.accent },
  exerciseCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  exerciseCardBody: { marginTop: Spacing.md, gap: Spacing.xs },

  setRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, paddingVertical: 3 },
  setNum: { width: 20, textAlign: 'center' },
  setMain: { flex: 1 },
  deleteBtn: { padding: Spacing.xs },

  logForm: { borderTopWidth: 1, borderTopColor: Colors.divider, paddingTop: Spacing.md, marginTop: Spacing.xs },
  logRow: { flexDirection: 'row', alignItems: 'flex-end', gap: Spacing.xs },
  logField: { flex: 2, gap: 4 },
  logFieldSm: { flex: 1 },
  logInput: {
    borderWidth: 1.5,
    borderColor: Colors.border,
    borderRadius: Radius.md,
    paddingHorizontal: Spacing.sm,
    paddingVertical: Spacing.xs + 2,
    fontSize: FontSize.md,
    color: Colors.text,
    backgroundColor: Colors.surface,
    minHeight: 40,
    textAlign: 'center',
  },
  logBtn: { minWidth: 52 },

  pickerOverlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    zIndex: 100,
    backgroundColor: 'rgba(27,42,65,0.4)',
    padding: Spacing.lg,
    justifyContent: 'flex-end',
  },
  picker: { maxHeight: '80%', gap: Spacing.md },
  pickerHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  pickerList: { maxHeight: 300 },
  exerciseOption: {
    paddingVertical: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
});
