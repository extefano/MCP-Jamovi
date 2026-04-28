# PLAN-001: Arquitectura Tecnica para MCP jamovi

Estado: Ready for Task Breakdown  
Fecha: 2026-04-27

## 1) Objetivo Tecnico

Implementar una arquitectura stateful y trazable para ejecutar analisis `jmv` via MCP, con traduccion GUI derivada de AST `*.u.yaml` y validacion estricta de contratos `*.a.yaml`.

## 2) Arquitectura por Fases

### Fase 1: Motor de Persistencia (Stateful R Session)

Componentes:

- `r_bridge.py`: gestor de sesiones R en memoria.
- `session_store` en Python: `Dict[str, SessionHandle]`.

Diseno:

- Crear `load_dataset_to_memory(file_path) -> session_id`.
- Asociar `session_id` a referencia de `data.frame` cargado.
- Reutilizar `session_id` en analisis subsecuentes.
- Definir politica minima de expiracion por inactividad.

Entregable:

- API interna estable para cargar, consultar y liberar sesiones.

### Prioridades Técnicas Inmediatas

Este plan prioriza el cierre rápido de tres brechas técnicas identificadas como bloqueantes para la siguiente iteración de implementación. Cada ítem incluye objetivos, tareas mínimas, criterios de aceptación y dependencias.

- SESS-MAN-01 — Gestor de Sesiones (High)
	- Objetivo: Entregar un `session manager` robusto, concurrente y con TTL que permita cargar datasets en R y reutilizar `session_id` sin reenviar rutas.
	- Tareas mínimas:
		1. Formalizar API: `load_dataset_to_memory(dataset_path) -> session_id`, `get_session_dataset_path(session_id)`, `release_session(session_id)`, `cleanup_expired_sessions()`.
		2. Implementar `SessionHandle` y `session_store` con bloqueo (threading.Lock) y limpieza por TTL.
		3. Añadir pruebas unitarias para carga, acceso concurrente, liberación y expiración (tests de fronteras: inexistente/expirado).
	- Criterios de aceptación:
		- Tests unitarios cubren casos de uso requeridos y pasan localmente.
		- `get_session_dataset_path` lanza error claro para `session_id` inválido/expirado.
		- G1 (ninguna herramienta usa `dataset_path` si existe `session_id`) verificado por pruebas.
	- Dependencias: Ninguna (prioridad más alta).

- DATA-SER-03 — Serialización de Resultados (High)
	- Objetivo: Garantizar transformación determinista de objetos R6 a JSON plano, con truncado seguro y representación Markdown legible.
	- Tareas mínimas:
		1. Definir contrato de salida: campos obligatorios `analysis`, `tables[]`, `markdown`, `dataset_path`, `session_id`.
		2. Implementar funciones de serialización: truncado por tamaño (`TABLE_JSON_LIMIT_BYTES`), enriquecimiento `markdown` a partir de tablas y flag `truncated` + `original_size_bytes`.
		3. Añadir tests que validen truncado y formato final (incluyendo encoding UTF-8).
	- Criterios de aceptación:
		- Contrato JSON validado por tests automáticos (SC-03 related).
		- Tablas grandes se truncarán y marcarán con `truncated: true` y `original_size_bytes`.
	- Dependencias: Requiere `SESS-MAN-01` para pruebas end-to-end.

- ERR-MAP-02 — Mapeo de Errores R a JSON-RPC (High)
	- Objetivo: Completar y formalizar la tabla de mapeo de errores R -> códigos JSON-RPC con mensajes localizados y `suggested_action`.
	- Tareas mínimas:
		1. Revisar y ampliar `_map_r_error` con patrones críticos (ej. singular matrix, niveles, missing values, not a factor).
		2. Añadir `AnalysisExecutionError` con serialización `to_dict()` y cobertura en `server.py` para retornar payloades consistentes.
		3. Pruebas unitarias que simulan stderr de R y verifican código, tipo y `suggested_action`.
	- Criterios de aceptación:
		- Cobertura de al menos 3 errores críticos y paso de tests automatizados.
		- Respuestas de endpoints incluyen campo `error` con `code`, `type`, `message`, `suggested_action`.
	- Dependencias: Independiente de `DATA-SER-03`, pero se valida en integración con los payloads serializados.

Entrega y roadmap corto (2 sprints)

- Sprint A (3-5 días): Entregar SESS-MAN-01 con cobertura de tests unitarios y pequeñas pruebas E2E simuladas.
- Sprint B (3-5 días): Entregar DATA-SER-03 + ERR-MAP-02 y ejecutar integración local: `jmv_ttestIS` con `session_id` produce payload conforme al contrato.

Riesgos residuales:

- Fuga de memoria por sesiones no liberadas → mitigar con tests de carga y TTL agresivo en CI.
- Inconsistencias de encoding en serialización → validar con fixtures UTF-8 y tablas grandes.

### Fase 2: Motor de Traduccion GUI (GUI Translation Service)

Componentes:

- Nuevo `gui_parser.py` o `yaml_reader.py`.
- Uso de `pyyaml` para parsear `*.u.yaml`.

Diseno:

- Dado `analysis_name` y opciones, localizar `analysis.u.yaml`.
- Recorrer AST para encontrar `name` de cada parametro y su `title` visible.
- Generar instruccion natural con ruta GUI y asignacion de variables a controles.

Entregable:

- Servicio determinista `build_gui_instructions(analysis, options)` basado en YAML.

### Fase 3: Herramientas MCP (Tool Endpoints)

Componentes:

- `models.py`: esquemas Pydantic por analisis.
- `server.py`: endpoints MCP conectados a bridge y gui translator.

Diseno:

- Implementar esquema exacto para `jmv_ttestIS` segun `ttestIS.a.yaml`.
- Exigir `session_id` para ejecucion (no `dataset_path` por defecto en runtime estable).
- Ejecutar analisis en R con data.frame ya residente.
- Parsear resultados R6 a `tables[]` y `markdown`.

Entregable:

- Endpoint `jmv_ttestIS` funcional con validacion, ejecucion y serializacion.

## 3) Secuencia Operativa End-to-End

1. Cliente invoca `tool_load_dataset` con `file_path`.
2. MCP valida ruta y carga dataset en R.
3. MCP retorna `session_id`.
4. Cliente invoca `jmv_ttestIS` con `session_id` y opciones.
5. Bridge ejecuta `jmv::ttestIS(...)` contra dataset en memoria.
6. Parser serializa tablas R6 a JSON plano + Markdown.
7. GUI parser genera guia paso a paso.
8. MCP responde payload consolidado.

## 4) Estrategia de Errores

- Interceptor central de stderr/errores R.
- Tabla de mapeo estatico a JSON-RPC.
- Siempre incluir `suggested_action`.
- Mantener fallback uniforme `-32000` para no mapeados.

## 5) Riesgos y Mitigaciones

Riesgo: fuga de memoria por sesiones no liberadas.  
Mitigacion: TTL + limpieza periodica.

Riesgo: inconsistencia entre `*.a.yaml` y esquema manual Pydantic.  
Mitigacion: prueba de contrato que compare campos requeridos.

Riesgo: traducciones GUI ambiguas por AST complejo.  
Mitigacion: tests con fixtures reales de `descriptives.u.yaml` y `ttestIS.u.yaml`.

## 6) Definition of Done de la Iteracion

- Sesiones R persistentes operativas con `session_id`.
- `jmv_ttestIS` integrado de extremo a extremo.
- GUI translation basado en parseo YAML real.
- Error mapping documentado e implementado para casos criticos.
- Tests unitarios y de integracion minimos en verde para fases 1-3.
