import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { useFocusEffect, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { supabase } from '@/lib/supabase';
import { Text } from '@/components/ui/Text';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Colors, Spacing } from '@/constants/theme';

interface DashboardStats {
  weeklySessions: number;
  weeklyVolume: number;
  totalSessions: number;
  lastWorkout: string | null;
}

export default function HomeScreen() {
  const router = useRouter();
  const [userEmail, setUserEmail] = useState('');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [hasActiveSession, setHasActiveSession] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  async function loadData() {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    setUserEmail(user.email ?? '');

    // Check for active session
    const { data: activeSessions } = await supabase
      .from('workout_sessions')
      .select('session_id')
      .eq('user_id', user.id)
      .is('end_time', null)
      .limit(1);
    setHasActiveSession((activeSessions?.length ?? 0) > 0);

    // Weekly stats (last 7 days)
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);

    const { data: sessions } = await supabase
      .from('workout_sessions')
      .select('session_id, start_time, end_time')
      .eq('user_id', user.id)
      .not('end_time', 'is', null)
      .gte('start_time', weekAgo.toISOString())
      .order('start_time', { ascending: false });

    const { count: totalCount } = await supabase
      .from('workout_sessions')
      .select('session_id', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .not('end_time', 'is', null);

    // Volume: sum weight_kg * reps across sets in this week's sessions
    let weeklyVolume = 0;
    if (sessions && sessions.length > 0) {
      const sessionIds = sessions.map(s => s.session_id);
      const { data: executions } = await supabase
        .from('exercise_executions')
        .select('execution_id')
        .in('session_id', sessionIds);

      if (executions && executions.length > 0) {
        const execIds = executions.map(e => e.execution_id);
        const { data: sets } = await supabase
          .from('sets')
          .select('weight_kg, reps')
          .in('execution_id', execIds);

        weeklyVolume = (sets ?? []).reduce((acc, s) => acc + s.weight_kg * s.reps, 0);
      }
    }

    const lastSession = sessions?.[0];
    const lastWorkout = lastSession
      ? new Date(lastSession.start_time).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
      : null;

    setStats({
      weeklySessions: sessions?.length ?? 0,
      weeklyVolume: Math.round(weeklyVolume),
      totalSessions: totalCount ?? 0,
      lastWorkout,
    });
  }

  useFocusEffect(useCallback(() => { loadData(); }, []));

  async function handleRefresh() {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }

  async function handleSignOut() {
    await supabase.auth.signOut();
  }

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text variant="h2">GymChat 💪</Text>
            <Text variant="bodySmall" color={Colors.textSecondary}>{userEmail}</Text>
          </View>
          <TouchableOpacity onPress={handleSignOut}>
            <Text variant="bodySmall" color={Colors.textSecondary}>Sign out</Text>
          </TouchableOpacity>
        </View>

        {/* Active session banner */}
        {hasActiveSession && (
          <Card style={styles.activeBanner}>
            <View style={styles.activeBannerRow}>
              <View style={styles.activeDot} />
              <Text variant="body" weight="semibold">Workout in progress</Text>
            </View>
            <Button
              label="Continue workout"
              onPress={() => router.push('/(tabs)/workout')}
              size="sm"
              style={styles.continueBtn}
            />
          </Card>
        )}

        {/* Weekly stats */}
        <Text variant="label" style={styles.sectionLabel}>This week</Text>
        <View style={styles.statsRow}>
          <StatCard label="Sessions" value={String(stats?.weeklySessions ?? '—')} />
          <StatCard
            label="Volume"
            value={stats ? `${(stats.weeklyVolume / 1000).toFixed(1)}t` : '—'}
            sub="kg lifted"
          />
          <StatCard label="All time" value={String(stats?.totalSessions ?? '—')} sub="sessions" />
        </View>

        {/* Last workout */}
        {stats?.lastWorkout && (
          <>
            <Text variant="label" style={styles.sectionLabel}>Last workout</Text>
            <Card>
              <Text variant="body">{stats.lastWorkout}</Text>
            </Card>
          </>
        )}

        {/* Quick actions */}
        <Text variant="label" style={styles.sectionLabel}>Quick actions</Text>
        <View style={styles.actions}>
          <Button
            label="Start workout"
            onPress={() => router.push('/(tabs)/workout')}
            fullWidth
            size="lg"
          />
          <Button
            label="View history"
            onPress={() => router.push('/(tabs)/history')}
            variant="secondary"
            fullWidth
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <Card style={styles.statCard} padded={false}>
      <View style={styles.statInner}>
        <Text variant="h2" color={Colors.accent}>{value}</Text>
        <Text variant="bodySmall" weight="semibold">{label}</Text>
        {sub && <Text variant="caption">{sub}</Text>}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  scroll: { padding: Spacing.lg, gap: Spacing.md },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: Spacing.xs },
  sectionLabel: { marginTop: Spacing.xs },
  statsRow: { flexDirection: 'row', gap: Spacing.sm },
  statCard: { flex: 1 },
  statInner: { padding: Spacing.md, alignItems: 'center', gap: 2 },
  actions: { gap: Spacing.sm },
  activeBanner: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: Colors.successLight, borderColor: Colors.success },
  activeBannerRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  activeDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: Colors.success },
  continueBtn: { marginLeft: Spacing.sm },
});
