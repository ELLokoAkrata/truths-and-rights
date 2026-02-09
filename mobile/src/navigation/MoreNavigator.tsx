import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { MoreMenuScreen } from '../screens/MoreMenuScreen';
import { MythsScreen } from '../screens/MythsScreen';
import { ContactsScreen } from '../screens/ContactsScreen';
import { AboutScreen } from '../screens/AboutScreen';
import type { MoreStackParamList } from './types';

const Stack = createNativeStackNavigator<MoreStackParamList>();

export function MoreNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: Colors.surface },
        headerTintColor: Colors.textPrimary,
        headerTitleStyle: { fontWeight: '600' },
        contentStyle: { backgroundColor: Colors.background },
      }}
    >
      <Stack.Screen
        name="MoreMenu"
        component={MoreMenuScreen}
        options={{ title: 'Mas' }}
      />
      <Stack.Screen
        name="Myths"
        component={MythsScreen}
        options={{ title: 'Mitos y Realidades' }}
      />
      <Stack.Screen
        name="Contacts"
        component={ContactsScreen}
        options={{ title: 'Contactos de Emergencia' }}
      />
      <Stack.Screen
        name="About"
        component={AboutScreen}
        options={{ title: 'Acerca de' }}
      />
    </Stack.Navigator>
  );
}
