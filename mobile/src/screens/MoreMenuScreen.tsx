import React from 'react';
import { View, Text, StyleSheet, Pressable, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { Colors } from '../constants/colors';
import { Typography } from '../constants/typography';
import type { MoreStackParamList } from '../navigation/types';

type Nav = NativeStackNavigationProp<MoreStackParamList>;

interface MenuItemProps {
  title: string;
  subtitle: string;
  onPress: () => void;
}

function MenuItem({ title, subtitle, onPress }: MenuItemProps) {
  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => [styles.menuItem, pressed && styles.pressed]}
      accessibilityLabel={title}
      accessibilityHint={subtitle}
      accessibilityRole="button"
    >
      <Text style={styles.menuTitle}>{title}</Text>
      <Text style={styles.menuSubtitle}>{subtitle}</Text>
    </Pressable>
  );
}

export function MoreMenuScreen() {
  const navigation = useNavigation<Nav>();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <MenuItem
        title="Mitos y Realidades"
        subtitle="Creencias comunes desmentidas"
        onPress={() => navigation.navigate('Myths')}
      />
      <MenuItem
        title="Contactos de Emergencia"
        subtitle="Telefonos de ayuda y denuncia"
        onPress={() => navigation.navigate('Contacts')}
      />
      <MenuItem
        title="Acerca de"
        subtitle="Version, fuentes y disclaimer"
        onPress={() => navigation.navigate('About')}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    paddingVertical: 8,
  },
  menuItem: {
    backgroundColor: Colors.surface,
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    minHeight: 64,
    justifyContent: 'center',
  },
  pressed: {
    backgroundColor: Colors.surfaceElevated,
  },
  menuTitle: {
    ...Typography.bodyBold,
    color: Colors.textPrimary,
  },
  menuSubtitle: {
    ...Typography.bodySmall,
    color: Colors.textSecondary,
    marginTop: 2,
  },
});
