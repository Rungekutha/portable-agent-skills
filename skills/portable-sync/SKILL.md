---
name: portable-sync
description: Comprobar y mantener sincronizadas las skills instaladas en Codex y Claude sin sobrescribir cambios ajenos.
---

# Sincronización entre Codex y Claude

Cuando el usuario pida comprobar o actualizar el paquete, localiza el bundle canónico y las carpetas de skills de ambas herramientas. Ejecuta el verificador incluido en el paquete para comparar hashes de cada SKILL.md con el manifiesto. Informa por separado: fuente válida, instalación Codex, instalación Claude, descubrimiento por cada app y uso real. Si falta una herramienta, ofrece instalarla cuando esté disponible; la carpeta existente no prueba que la aplicación la haya cargado.

Para reparar, muestra el diff o la lista exacta de archivos y solicita autorización para esa instalación. Copia desde el bundle verificado, no desde la copia que pudiera haber cambiado. No sobrescribas skills preexistentes de terceros; una colisión requiere una decisión explícita. No crees schedules por inferencia ni sincronices conversaciones, credenciales o configuración privada.

## Preferencias y alcance

Usa primero las preferencias no secretas elegidas al instalar en portable-tools/references/profile.json. Una preferencia vacía significa sin decidir. Sugiere opciones pertinentes y pregunta sólo cuando una elección cambie materialmente el resultado; nunca exige una marca, cuenta, nube o repositorio concreto. Una conexión configurada no prueba acceso ni ejecución. Antes de una escritura identifica cuenta, objeto y destino; después relee el resultado. No infieras permiso para pagos, publicaciones, borrados o ampliaciones de acceso.
