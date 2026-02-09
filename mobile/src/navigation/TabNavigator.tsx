import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Text, View, StyleSheet } from 'react-native';
import { Colors } from '../constants/colors';
import { HomeScreen } from '../screens/HomeScreen';
import { RightsListScreen } from '../screens/RightsListScreen';
import { EmergencyScreen } from '../screens/EmergencyScreen';
import { MoreNavigator } from './MoreNavigator';
import type { TabParamList } from './types';

const Tab = createBottomTabNavigator<TabParamList>();

function TabIcon({ label, focused }: { label: string; focused: boolean }) {
  return (
    <View style={styles.iconContainer}>
      <Text
        style={[styles.iconText, focused && styles.iconTextActive]}
        accessibilityLabel={label}
      >
        {label === 'Inicio' ? '●' : label === 'Derechos' ? '◆' : label === 'Emergencia' ? '▲' : '≡'}
      </Text>
    </View>
  );
}

export function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: Colors.textMuted,
        tabBarLabelStyle: styles.tabLabel,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarLabel: 'Inicio',
          tabBarIcon: ({ focused }) => <TabIcon label="Inicio" focused={focused} />,
          tabBarAccessibilityLabel: 'Inicio',
        }}
      />
      <Tab.Screen
        name="Rights"
        component={RightsListScreen}
        options={{
          tabBarLabel: 'Derechos',
          tabBarIcon: ({ focused }) => <TabIcon label="Derechos" focused={focused} />,
          tabBarAccessibilityLabel: 'Lista de derechos',
        }}
      />
      <Tab.Screen
        name="Emergency"
        component={EmergencyScreen}
        options={{
          tabBarLabel: 'Emergencia',
          tabBarIcon: ({ focused }) => <TabIcon label="Emergencia" focused={focused} />,
          tabBarAccessibilityLabel: 'Estado de emergencia',
        }}
      />
      <Tab.Screen
        name="More"
        component={MoreNavigator}
        options={{
          tabBarLabel: 'Mas',
          tabBarIcon: ({ focused }) => <TabIcon label="Mas" focused={focused} />,
          tabBarAccessibilityLabel: 'Mas opciones',
        }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: Colors.surface,
    borderTopColor: Colors.border,
    borderTopWidth: 1,
    height: 60,
    paddingBottom: 8,
    paddingTop: 4,
  },
  tabLabel: {
    fontSize: 11,
    fontWeight: '600',
  },
  iconContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 24,
    height: 24,
  },
  iconText: {
    fontSize: 18,
    color: Colors.textMuted,
  },
  iconTextActive: {
    color: Colors.primary,
  },
});
