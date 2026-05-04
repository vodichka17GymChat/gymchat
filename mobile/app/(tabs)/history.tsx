import React, { useState, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { useFocusEffect } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { supabase } from '@/lib/supabase';
import { Text } from '@/components/ui/Text';
import { Card } from '@/components/ui/Card';
import { Colors, Spacing } from '@/constants/theme';

interface SessionSummary {
  session_id: number;
  workout_type: string | null;
  start_time: string;
  end_time: string;
  exercise_count: number;
  set_count: number;
  volume_kg: number;
}

export default function HistoryScreen() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [exercises, setExercises] = useState<Record<number, { name: string; sets: number }[]>>({});
  const [refreshing, setRefreshing] = useState(false);

  async function loadSessions() {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const { data: sessionRows } = await supabase
      .from('workout_sessions')
      .select('session_id, workout_type, start_time, end_time')
      .eq('user_id', user.id)
      .not('end_time', 'is', null)
      .order('start_time', { ascending: false })
      .limit(30);

    if (!sessionRows?.length) { setSessions([]); return; }

    const summaries: SessionSummary[] = await Promise.all(
      sessionRows.map(async (s) => {
        const { data: execs } = await supabase
          .from('exercise_executions')
          .select('execution_id')
          .eq('session_id', s.session_id);

        const execIds = (execs ?? []).map(e => e.execution_id);
        let setCount = 0;
        let volume = 0;

        if (execIds.length > 0) {
          const { data: sets } = await supabase
            .from('sets')
            .select('weight_kg, reps')
            .in('execution_id', execIds);
          setCount = sets?.length ?? 0;
          volume = (sets ?? []).reduce((acc, s) => acc + s.weight_kg * s.reps, 0);
        }

        return {
          session_id: s.session_id,
          workout_type: s.workout_type,
          start_time: s.start_time,
          end_time: s.end_time,
          exercise_count: execs?.length ?? 0,
          set_count: setCount,
          volume_kg: Math.round(volume),
        };
      })
    );

    setSessions(summaries);
  }

  async function loadExercisesForSession(sessionId: number) {
    if (exercises[sessionId]) return;

    const { data: execs } = await supabase
      .from('exercise_executions')
      .select('execution_id, exercise_id, exercises(exercise_name)')
      .eq('session_id', sessionId)
      .order('execution_order');

    if (!execs) return;

    const result = await Promise.all(
      execs.map(async (ex) => {
        const { count } = await supabase
          .from('sets')
          .select('set_id', { count: 'exact', head: true })
          .eq('execution_id', ex.execution_id);

        const name = (ex.exercises as { exercise_name: string } | null)?.exercise_name ?? 'Unknown';
        return { name, sets: count ?? 0 };
      })
    );

    setExercises(prev => ({ ...prev, [sessionId]: result }));
  }

  useFocusEffect(useCallback(() => { loadSessions(); }, []));

  async function handleRefresh() {
    setRefreshing(true);
    await loadSessions();
    setRefreshing(false);
  }

  function toggleSession(id: number) {
    if (expandedId === id) {
      setExpandedId(null);
    } else {
      setExpandedId(id);
      loadExercisesForSession(id);
    }
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
      >
        <Text variant="h2" style={styles.title}>History</Text>

        {sessions.length === 0 ? (
          <Card>
            <Text variant="body" color={Colors.textSecondary}>
              No completed workouts yet. Finish your first session to see it here.
            </Text>
          </Card>
        ) : (
          sessions.map(s => {
            const isExpanded = expandedId === s.session_id;
            const date = new Date(s.start_time);
            const dateStr = date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
            const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

            return (
              <TouchableOpacity key={s.session_id} onPress={() => toggleSession(s.session_id)} activeOpacity={0.8}>
                <Card style={isExpanded ? styles.expandedCard : undefined}>
                  <View style={styles.sessionHeader}>
                    <View style={styles.sessionInfo}>
                      <Text variant="body" weight="semibold">
                        {s.workout_type ?? 'Workout'}
                      </Text>
                      <Text variant="caption">{dateStr} · {timeStr}</Text>
                    </View>
                    <Text variant="caption" color={Colors.textMuted}>{isExpanded ? '▲' : '▼'}</Text>
                  </View>

                  <View style={styles.sessionMeta}>
                    <MetaChip label={`${s.exercise_count} exercises`} />
                    <MetaChip label={`${s.set_count} sets`} />
                    <MetaChip label={`${s.volume_kg.toLocaleString()} kg`} />
                  </View>

                  {isExpanded && exercises[s.session_id] && (
                    <View style={styles.exerciseList}>
                      {exercises[s.session_id].map((ex, i) => (
                        <View key={i} style={styles.exerciseRow}>
                          <Text variant="bodySmall">{ex.name}</Text>
                          <Text variant="caption" color={Colors.textMuted}>{ex.sets} sets</Text>
                        </View>
                      ))}
                    </View>
                  )}
                </Card>
              </TouchableOpacity>
            );
          })
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function MetaChip({ label }: { label: string }) {
  return (
    <View style={chipStyles.chip}>
      <Text variant="caption" color={Colors.textSecondary}>{label}</Text>
    </View>
  );
}

const chipStyles = StyleSheet.create({
  chip: {
    backgroundColor: Colors.accentLight,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 99,
  },
});

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { padding: Spacing.lg, gap: Spacing.sm },
  title: { marginBottom: Spacing.xs },
  sessionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  sessionInfo: { gap: 2 },
  sessionMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs, marginTop: Spacing.sm },
  expandedCard: { borderColor: Colors.accent },
  exerciseList: { marginTop: Spacing.md, gap: Spacing.xs, borderTopWidth: 1, borderTopColor: Colors.divider, paddingTop: Spacing.md },
  exerciseRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
});
