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
