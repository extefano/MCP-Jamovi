# TASKS-001: Checklist Binario de Ejecucion

Estado: Ready for Implementation  
Fecha: 2026-04-27

Regla: cada tarea es atomica y verificable. No se inicia codificacion hasta cerrar este checklist de planificacion.

## Fase 0 - Gobernanza SDD

- [x] T0.1 Crear `spec.md`.
- [x] T0.2 Crear `plan.md`.
- [x] T0.3 Crear `tasks.md`.

## Fase 1 - Persistencia de Sesion R

- [ ] T1.1 Agregar en `r_bridge.py` metodo `tool_load_dataset(file_path) -> session_id`.
- [ ] T1.2 Definir `session_store` global (`session_id` -> referencia dataset en R).
- [ ] T1.3 [P] Implementar `get_session(session_id)` con validacion de existencia.
- [ ] T1.4 [P] Agregar liberacion de sesion y/o limpieza por inactividad (TTL).
- [ ] T1.5 [P] Crear pruebas unitarias para carga, reutilizacion y expiracion de sesion.

## Fase 2 - Traduccion GUI por YAML

- [x] T2.1 Crear `yaml_reader.py` o `gui_parser.py` para lectura de `*.u.yaml`.
- [x] T2.2 [P] Implementar recorrido AST para resolver `name -> title` de controles.
- [x] T2.3 [P] Programar plantilla de salida:
  `Abre jamovi -> Analyses -> <Ruta> -> mueve <Vars> a <Control_Title>`.
- [x] T2.4 [P] Integrar parser YAML en `build_gui_instructions(...)`.
- [x] T2.5 [P] Crear tests unitarios usando mock de `descriptives.u.yaml`.

## Fase 3 - Herramienta jmv_ttestIS

- [x] T3.1 Implementar esquema Pydantic exacto para `jmv_ttestIS` segun `ttestIS.a.yaml`.
- [x] T3.2 [P] Exigir `session_id` en request de herramientas de analisis.
- [x] T3.3 [P] Conectar endpoint `jmv_ttestIS` al bridge stateful.
- [x] T3.4 [P] Parsear salida R6 a arreglo de diccionarios JSON estandar.
- [x] T3.5 [P] Incluir `gui_instructions` generado por parser YAML real.
- [x] T3.6 [P] Agregar pruebas de integracion de endpoint (ok + errores esperados).
- [ ] T3.7 [P] Implementar truncamiento seguro de tablas JSON a 2MB y flags `truncated` / `original_size_bytes`.

## Fase 4 - Error Mapping y Hardening

- [x] T4.1 Unificar tabla de mapeo de errores R con codigos JSON-RPC `-32602` para errores de datos/parametros.
- [x] T4.2 [P] Implementar mensajes con `suggested_action` en todas las rutas de error.
- [x] T4.3 [P] Probar al menos 2 errores mapeados: `singular matrix` y `must have exactly 2 levels`.

## Fase 5 - Cobertura de Success Criteria (SC-01, SC-03)

- [ ] T5.1 Implementar enforcement de volumen `/data` en modo read-only en `Dockerfile`: validar que volumne se monta con flag `ro`.
- [ ] T5.2 [P] Crear test de integracion automatizado en `tests/` que valida rechazo de escritura en `/data`.
- [ ] T5.3 [P] Crear validador de contrato JSON en `server.py` que garantiza inclusion de `analysis_name` y `session_id` en toda respuesta.
- [ ] T5.4 [P] Implementar fixture de prueba que ejecuta todas las herramientas MCP y valida compliance de esquema.
- [ ] T5.5 [P] Agregar test de performance/latencia p95 para reutilizacion de `session_id` en `tests/`.
- [ ] T5.6 Ejecutar suite completa de tests y validar gates SC-01, SC-02, SC-03 antes de marcar fase como completa.

## Gates de Cierre

- [x] G1 Ninguna herramienta ejecuta con `dataset_path` directo cuando exista `session_id` activo.
- [x] G2 `jmv_ttestIS` responde con `tables`, `markdown`, `gui_instructions`.
- [x] G3 Traduccion GUI sale de parseo YAML y no de mapa hardcodeado.
- [x] G4 Tests minimos de fases 1-4 pasan en CI/local.
- [ ] G5 Volumen `/data` rechaza escritura y test automatizado lo valida (SC-01).
- [ ] G6 Esquema JSON de respuesta incluye obligatoriamente `analysis_name` y `session_id` (SC-03).
- [ ] G7 Latencia p95 para reutilizacion de `session_id` es menor a 500ms con datasets hasta 100K filas (SC-02).

## Orden de Ejecucion Obligatorio

1. Completar Fase 1.
2. Completar Fase 2.
3. Completar Fase 3.
4. Completar Fase 4.
5. Completar Fase 5 (Success Criteria).
6. Validar Gates G1-G7.

No saltar fases. No abrir nueva implementacion de analisis `jmv` hasta cerrar este ciclo. Tareas marcadas con [P] en la misma fase pueden ejecutarse en paralelo una vez que sus dependencias esten resueltas.
