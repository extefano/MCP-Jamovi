# TASKS-001: Checklist Binario de Ejecucion

Estado: Ready for Implementation  
Fecha: 2026-04-27

Regla: cada tarea es atomica y verificable. No se inicia codificacion hasta cerrar este checklist de planificacion.

## Fase 0 - Gobernanza SDD

- [x] T0.1 Crear `spec.md`.
- [x] T0.2 Crear `plan.md`.
- [x] T0.3 Crear `tasks.md`.

## Fase 1 - Persistencia de Sesion R

- [x] T1.1 Agregar en `r_bridge.py` metodo `load_dataset_to_memory(file_path) -> session_id`.
- [x] T1.2 Definir `session_store` global (`session_id` -> referencia dataset en R).
- [x] T1.3 Implementar `get_session(session_id)` con validacion de existencia.
- [x] T1.4 Agregar liberacion de sesion y/o limpieza por inactividad (TTL).
- [x] T1.5 Crear pruebas unitarias para carga, reutilizacion y expiracion de sesion.

## Fase 2 - Traduccion GUI por YAML

- [x] T2.1 Crear `yaml_reader.py` o `gui_parser.py` para lectura de `*.u.yaml`.
- [x] T2.2 Implementar recorrido AST para resolver `name -> title` de controles.
- [x] T2.3 Programar plantilla de salida:
  `Abre jamovi -> Analyses -> <Ruta> -> mueve <Vars> a <Control_Title>`.
- [x] T2.4 Integrar parser YAML en `build_gui_instructions(...)`.
- [x] T2.5 Crear tests unitarios usando mock de `descriptives.u.yaml`.

## Fase 3 - Herramienta jmv_ttestIS

- [x] T3.1 Implementar esquema Pydantic exacto para `jmv_ttestIS` segun `ttestIS.a.yaml`.
- [x] T3.2 Exigir `session_id` en request de herramientas de analisis.
- [x] T3.3 Conectar endpoint `jmv_ttestIS` al bridge stateful.
- [x] T3.4 Parsear salida R6 a arreglo de diccionarios JSON estandar.
- [x] T3.5 Incluir `gui_instructions` generado por parser YAML real.
- [x] T3.6 Agregar pruebas de integracion de endpoint (ok + errores esperados).

## Fase 4 - Error Mapping y Hardening

- [x] T4.1 Unificar tabla de mapeo de errores R con codigos JSON-RPC `-32602` para errores de datos/parametros.
- [x] T4.2 Implementar mensajes con `suggested_action` en todas las rutas de error.
- [x] T4.3 Probar al menos 2 errores mapeados: `singular matrix` y `must have exactly 2 levels`.

## Gates de Cierre

- [x] G1 Ninguna herramienta ejecuta con `dataset_path` directo cuando exista `session_id` activo.
- [x] G2 `jmv_ttestIS` responde con `tables`, `markdown`, `gui_instructions`.
- [x] G3 Traduccion GUI sale de parseo YAML y no de mapa hardcodeado.
- [x] G4 Tests minimos de fases 1-4 pasan en CI/local.

## Orden de Ejecucion Obligatorio

1. Completar Fase 1.
2. Completar Fase 2.
3. Completar Fase 3.
4. Completar Fase 4.
5. Validar Gates G1-G4.

No saltar fases. No abrir nueva implementacion de analisis `jmv` hasta cerrar este ciclo.
