import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { DatabaseProvider } from './src/database/DatabaseProvider';
import { RootNavigator } from './src/navigation/RootNavigator';
import { loadPersistedState } from './src/store/useAppStore';

export default function App() {
  useEffect(() => {
    loadPersistedState();
  }, []);

  return (
    <DatabaseProvider>
      <StatusBar style="light" />
      <RootNavigator />
    </DatabaseProvider>
  );
}
