import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AppState {
  /** Timestamp del ultimo check de actualizacion. */
  lastUpdateCheck: number | null;
  setLastUpdateCheck: (ts: number) => void;

  /** Preferencia: mostrar disclaimer. */
  disclaimerAccepted: boolean;
  setDisclaimerAccepted: (v: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  lastUpdateCheck: null,
  setLastUpdateCheck: (ts) => {
    set({ lastUpdateCheck: ts });
    AsyncStorage.setItem('lastUpdateCheck', String(ts));
  },

  disclaimerAccepted: false,
  setDisclaimerAccepted: (v) => {
    set({ disclaimerAccepted: v });
    AsyncStorage.setItem('disclaimerAccepted', String(v));
  },
}));

/** Carga las preferencias persistidas al iniciar. */
export async function loadPersistedState(): Promise<void> {
  try {
    const [lastCheck, disclaimer] = await Promise.all([
      AsyncStorage.getItem('lastUpdateCheck'),
      AsyncStorage.getItem('disclaimerAccepted'),
    ]);

    useAppStore.setState({
      lastUpdateCheck: lastCheck ? Number(lastCheck) : null,
      disclaimerAccepted: disclaimer === 'true',
    });
  } catch {
    // Ignorar errores de lectura
  }
}
