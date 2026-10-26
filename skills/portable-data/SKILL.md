---
name: portable-data
description: Trabajar con datos estructurados, bases, tablas y análisis conservando fuentes y esquema.
---

# Datos estructurados

Determina qué pregunta debe contestarse, fuente, esquema, calidad y destino. Sugiere SQLite, Postgres, hojas de cálculo u otro servicio disponible según escala y preferencias; no exige Neon ni nube. Mantén los datos originales y registra transformaciones.

Antes de escribir en tablas, verifica identidad de base, llave, versión y filas afectadas. Usa transacciones o comparaciones de versión cuando haya concurrencia. Relee el registro exacto. Distingue cobertura de muestra, ausencia y error de acceso.

## Preferencias y alcance

Usa primero las preferencias no secretas elegidas al instalar en portable-tools/references/profile.json. Una preferencia vacía significa sin decidir. Sugiere opciones pertinentes y pregunta sólo cuando una elección cambie materialmente el resultado; nunca exige una marca, cuenta, nube o repositorio concreto. Una conexión configurada no prueba acceso ni ejecución. Antes de una escritura identifica cuenta, objeto y destino; después relee el resultado. No infieras permiso para pagos, publicaciones, borrados o ampliaciones de acceso.
