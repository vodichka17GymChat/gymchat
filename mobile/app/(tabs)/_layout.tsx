import { Tabs } from 'expo-router';
import { Colors, FontSize } from '@/constants/theme';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: Colors.accent,
        tabBarInactiveTintColor: Colors.textMuted,
        tabBarStyle: {
          backgroundColor: Colors.surface,
          borderTopColor: Colors.border,
          borderTopWidth: 1,
        },
        tabBarLabelStyle: { fontSize: FontSize.xs, marginBottom: 2 },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{ title: 'Home', tabBarIcon: ({ color }) => <TabIcon label="🏠" color={color} /> }}
      />
      <Tabs.Screen
        name="workout"
        options={{ title: 'Workout', tabBarIcon: ({ color }) => <TabIcon label="🏋️" color={color} /> }}
      />
      <Tabs.Screen
        name="history"
        options={{ title: 'History', tabBarIcon: ({ color }) => <TabIcon label="📊" color={color} /> }}
      />
      <Tabs.Screen
        name="profile"
        options={{ title: 'Profile', tabBarIcon: ({ color }) => <TabIcon label="👤" color={color} /> }}
      />
    </Tabs>
  );
}

function TabIcon({ label, color }: { label: string; color: string }) {
  const { Text } = require('react-native');
  return <Text style={{ fontSize: 20, color }}>{label}</Text>;
}
