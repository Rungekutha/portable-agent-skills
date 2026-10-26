# Skills portables para Codex y Claude

Este paquete reúne 22 skills independientes por capacidad. Conserva los principios reutilizables de coordinación, evidencia, apps, datos, documentos, comunicación, finanzas, salud, infraestructura y otras áreas. No contiene cuentas, chats, rutas personales, secretos ni decisiones de otra persona.

## Instalación

Si recibiste un enlace al repositorio, pégalo en Codex o Claude con esta petición: «Revisa este paquete e instálalo en Codex y Claude. Pregúntame mis preferencias opcionales y solicita mi permiso antes de copiar archivos». El agente debe mostrar la procedencia y ejecutar el instalador; el enlace por sí solo no ejecuta código.

1. Descarga el paquete desde el enlace compartido y extrae su carpeta.
2. Ejecuta `python3 install.py` desde esa carpeta.
3. El instalador detecta Codex y Claude, propone las rutas estándar de ambas aplicaciones, pregunta preferencias **opcionales** de herramientas y solicita permiso para instalar en las dos. No instala ni autentica servicios externos.
4. Ejecuta `python3 install.py --check` para comparar ambas copias con el manifiesto. Después abre cada aplicación y comprueba que reconoce una skill, por ejemplo `portable-landscape`. Una carpeta copiada no demuestra descubrimiento.

En una máquina con rutas no estándar, se pueden pasar `--codex-root RUTA` y `--claude-root RUTA`. El instalador no sobrescribe una skill existente con el mismo nombre; informa la colisión para revisarla. Las preferencias vacías quedan sin decidir y la skill preguntará sólo cuando la elección sea relevante.

## Mantenimiento

El bundle es la fuente de las instrucciones. `--check` detecta ausencias y diferencias de hash entre el bundle, Codex y Claude. Si hay una diferencia, revisa el archivo antes de instalar una nueva versión. El paquete no programa tareas periódicas, no sincroniza conversaciones ni copia credenciales. La skill `portable-sync` ayuda a resolver diferencias con autorización explícita.

## Herramientas

Consulta [catálogo de opciones](skills/portable-tools/references/tool-catalog.md). Son sugerencias por capacidad; ninguna marca es obligatoria. Las integraciones se conectan y autorizan por separado, y cada operación necesita verificar cuenta, objeto y destino.
