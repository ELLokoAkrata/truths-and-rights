# Metodología Legal / Legal Methodology

## ¿Cómo garantizamos que la información es correcta?

Una app de derechos con datos incorrectos es peor que no tener app. Por eso seguimos un proceso estricto.

---

## Cadena de verificación

```
Fuente oficial (SPIJ, TC, El Peruano)
       │
       ▼
Extracción del texto literal
       │
       ▼
Verificación de vigencia (¿ha sido modificada o derogada?)
       │
       ▼
Simplificación a lenguaje ciudadano
       │
       ▼
Revisión cruzada (mínimo 2 fuentes para datos críticos)
       │
       ▼
Revisión por abogado (ideal, no siempre posible)
       │
       ▼
Ingreso a la base de datos con fuente, fecha y URL
```

---

## Niveles de confianza

Cada dato legal tiene un nivel de confianza implícito:

### Nivel 1 — Texto constitucional o legal literal
- Fuente: texto exacto de la ley
- Ejemplo: "El plazo máximo de detención es 48 horas" (Art. 2.24.f Constitución)
- Confianza: máxima

### Nivel 2 — Jurisprudencia del TC o Corte IDH
- Fuente: sentencia publicada
- Ejemplo: "La actitud sospechosa como habilitante es inaceptable" (Exp. 00413-2022-PHC/TC)
- Confianza: alta (es vinculante)

### Nivel 3 — Interpretación doctrinaria consensuada
- Fuente: múltiples expertos coinciden
- Ejemplo: "Negarse al registro de pertenencias no constituye desobediencia"
- Confianza: alta pero requiere nota aclaratoria

### Nivel 4 — Recomendación práctica
- Fuente: experiencia de ONGs, defensores, práctica judicial
- Ejemplo: "Es recomendable colaborar con la identificación"
- Confianza: media (es consejo, no ley)

**Regla:** Los niveles 1 y 2 se presentan como hechos. Los niveles 3 y 4 se presentan con lenguaje condicional ("según la doctrina mayoritaria", "se recomienda").

---

## Actualización de datos

Las leyes cambian. Los decretos de emergencia se renuevan. La jurisprudencia evoluciona.

### Monitoreo automatizado

El proyecto cuenta con workflows de GitHub Actions que ejecutan verificaciones automaticas:

| Check | Frecuencia | Que verifica |
|---|---|---|
| Estado de emergencia | Semanal (lunes 9 AM Lima) | Decretos vencidos o por vencer (<7 dias) |
| Vigencia de fuentes | Quincenal (dia 1 y 15) | Fuentes modificadas o desactualizadas |
| Scrape completo | Mensual (dia 1) | Textos oficiales actualizados |
| Health check | Semanal | Accesibilidad de sitios gubernamentales |

**Principio clave:** Los workflows nunca modifican datos legales automaticamente. Solo crean Issues para revision humana. Los datos legales requieren verificacion de abogado.

Cada verificacion se registra en `data/PE/verification_history.jsonl` como audit trail.

### Monitoreo manual (complementario)
- Revisar El Peruano semanalmente para nuevos decretos
- Revisar el TC mensualmente para nuevas sentencias
- Verificar estados de emergencia vigentes (cambian cada 30-60 dias)

### Versionado
- Cada actualizacion de datos legales se documenta en CHANGELOG.md
- Los datos incluyen campo `updated_at` para rastrear frescura
- Los datos con mas de 6 meses sin verificacion se marcan para revision

### Proceso de actualizacion
1. Se detecta cambio legal (automaticamente via workflow o manualmente)
2. Se crea Issue con etiqueta `legal-data` + `urgent` si afecta derechos
3. Se verifica el cambio en la fuente oficial
4. Se actualiza la fuente en `legal_sources`
5. Se actualizan las situaciones, derechos y acciones afectadas
6. Se genera nueva version del .db
7. Se publica actualizacion de la app y el portal

---

## Qué NO hacemos

- **No damos asesoría legal.** La app informa derechos, no reemplaza a un abogado.
- **No interpretamos la ley.** Presentamos lo que dice la ley y la jurisprudencia.
- **No garantizamos resultados.** Conocer tus derechos no garantiza que la policía los respete.
- **No almacenamos casos personales.** Los reportes son anónimos y agregados.

## Disclaimer legal

Esta aplicación proporciona información legal de carácter general basada en la legislación peruana vigente. No constituye asesoría legal profesional. Para casos específicos, consulte con un abogado. Los creadores y contribuidores no son responsables por el uso que se dé a esta información.
