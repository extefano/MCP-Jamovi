# TASKS-001: Checklist Binario de Ejecucion

Estado: Ready for Implementation  
Fecha: 2026-04-27

Regla: cada tarea es atomica y verificable. No se inicia codificacion hasta cerrar este checklist de planificacion.

## Fase 0 - Gobernanza SDD

- [x] T0.1 Crear `.specify/spec.md`.
- [x] T0.2 Crear `.specify/plan.md`.
- [x] T0.3 Crear `.specify/tasks.md`.

## Fase 1 - Persistencia de Sesion R

- [ ] T1.1 Agregar en `r_bridge.py` metodo `load_dataset_to_memory(file_path) -> session_id`.
- [ ] T1.2 Definir `session_store` global (`session_id` -> referencia dataset en R).
- [ ] T1.3 Implementar `get_session(session_id)` con validacion de existencia.
- [ ] T1.4 Agregar liberacion de sesion y/o limpieza por inactividad (TTL).
- [ ] T1.5 Crear pruebas unitarias para carga, reutilizacion y expiracion de sesion.

## Fase 2 - Traduccion GUI por YAML

- [ ] T2.1 Crear `yaml_reader.py` o `gui_parser.py` para lectura de `*.u.yaml`.
- [ ] T2.2 Implementar recorrido AST para resolver `name -> title` de controles.
- [ ] T2.3 Programar plantilla de salida:
  `Abre jamovi -> Analyses -> <Ruta> -> mueve <Vars> a <Control_Title>`.
- [ ] T2.4 Integrar parser YAML en `build_gui_instructions(...)`.
- [ ] T2.5 Crear tests unitarios usando mock de `descriptives.u.yaml`.

## Fase 3 - Herramienta jmv_ttestIS

- [ ] T3.1 Implementar esquema Pydantic exacto para `jmv_ttestIS` segun `ttestIS.a.yaml`.
- [ ] T3.2 Exigir `session_id` en request de herramientas de analisis.
- [ ] T3.3 Conectar endpoint `jmv_ttestIS` al bridge stateful.
- [ ] T3.4 Parsear salida R6 a arreglo de diccionarios JSON estandar.
- [ ] T3.5 Incluir `gui_instructions` generado por parser YAML real.
- [ ] T3.6 Agregar pruebas de integracion de endpoint (ok + errores esperados).

## Fase 4 - Error Mapping y Hardening

- [ ] T4.1 Unificar tabla de mapeo de errores R con codigos JSON-RPC `-32602` para errores de datos/parametros.
- [ ] T4.2 Implementar mensajes con `suggested_action` en todas las rutas de error.
- [ ] T4.3 Probar al menos 2 errores mapeados: `singular matrix` y `must have exactly 2 levels`.

## Gates de Cierre

- [ ] G1 Ninguna herramienta ejecuta con `dataset_path` directo cuando exista `session_id` activo.
- [ ] G2 `jmv_ttestIS` responde con `tables`, `markdown`, `gui_instructions`.
- [ ] G3 Traduccion GUI sale de parseo YAML y no de mapa hardcodeado.
- [ ] G4 Tests minimos de fases 1-4 pasan en CI/local.

## Orden de Ejecucion Obligatorio

1. Completar Fase 1.
2. Completar Fase 2.
3. Completar Fase 3.
4. Completar Fase 4.
5. Validar Gates G1-G4.

No saltar fases. No abrir nueva implementacion de analisis `jmv` hasta cerrar este ciclo.
