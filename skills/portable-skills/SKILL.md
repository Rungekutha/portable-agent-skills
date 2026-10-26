---
name: portable-skills
description: Crear, instalar y revisar skills portables con nombres claros y dependencias explícitas.
---

# Skills reutilizables

Redacta cada skill para una capacidad concreta y un disparador distinguible. Mantén instrucciones breves, referencias condicionales y scripts sólo cuando hagan trabajo determinista útil. Evita incrustar identidades, rutas, cuentas, claves, repositorios o restricciones de un usuario en un paquete para otros.

Antes de instalar, muestra el conjunto exacto, pregunta preferencias de herramientas y pide permiso de instalación. Comprueba formato, colisiones, hashes y lectura real por el cliente. La existencia de una carpeta no prueba descubrimiento ni adopción.

## Preferencias y alcance

Usa primero las preferencias no secretas elegidas al instalar en portable-tools/references/profile.json. Una preferencia vacía significa sin decidir. Sugiere opciones pertinentes y pregunta sólo cuando una elección cambie materialmente el resultado; nunca exige una marca, cuenta, nube o repositorio concreto. Una conexión configurada no prueba acceso ni ejecución. Antes de una escritura identifica cuenta, objeto y destino; después relee el resultado. No infieras permiso para pagos, publicaciones, borrados o ampliaciones de acceso.
