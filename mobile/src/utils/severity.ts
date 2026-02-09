import { Colors } from '../constants/colors';

/**
 * Mapea severidad a color e icono.
 */

type Severity = 'low' | 'medium' | 'high' | 'critical';

interface SeverityInfo {
  color: string;
  label: string;
  icon: string;
}

const SEVERITY_MAP: Record<Severity, SeverityInfo> = {
  low: {
    color: Colors.severityLow,
    label: 'Bajo',
    icon: 'shield-checkmark-outline',
  },
  medium: {
    color: Colors.severityMedium,
    label: 'Medio',
    icon: 'alert-circle-outline',
  },
  high: {
    color: Colors.severityHigh,
    label: 'Alto',
    icon: 'warning-outline',
  },
  critical: {
    color: Colors.severityCritical,
    label: 'Critico',
    icon: 'alert-outline',
  },
};

export function getSeverityInfo(severity: string): SeverityInfo {
  return SEVERITY_MAP[severity as Severity] ?? SEVERITY_MAP.medium;
}
