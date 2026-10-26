---
name: portable-infrastructure
description: Gestionar repositorios, servidores y despliegues con identidad, costo y readback.
---

# Infraestructura

Determina host, cuenta, repositorio, entorno y objetivo. Sugiere local, nube o servidor existente según preferencias y costo; no exige un proveedor. Separa configuración, despliegue, servicio vivo y aceptación. Una máquina o perfil creado no prueba que el trabajo corra allí.

Antes de modificar infraestructura, verifica autoridad, alcance y posible costo. Aplica cambios acotados, conserva rollback y relee el recurso remoto. No actives jobs o workflows sin petición específica.

## Preferencias y alcance

Usa primero las preferencias no secretas elegidas al instalar en portable-tools/references/profile.json. Una preferencia vacía significa sin decidir. Sugiere opciones pertinentes y pregunta sólo cuando una elección cambie materialmente el resultado; nunca exige una marca, cuenta, nube o repositorio concreto. Una conexión configurada no prueba acceso ni ejecución. Antes de una escritura identifica cuenta, objeto y destino; después relee el resultado. No infieras permiso para pagos, publicaciones, borrados o ampliaciones de acceso.
