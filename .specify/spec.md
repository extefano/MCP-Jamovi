# SPEC-001: Pipeline SDD para MCP jamovi

Estado: Draft Ready for Planning  
Fecha: 2026-04-27  
Owner: MCP jamovi team

## 1) Objetivo

Definir un contrato determinista para exponer analisis de `jmv` a traves de MCP con:

- validacion estructural de entradas JSON-RPC,
- ejecucion headless en R,
- serializacion estable de resultados R6 a JSON/Markdown,
- traduccion inversa a pasos GUI de jamovi.

Ningun cambio de codigo Python/R esta permitido hasta completar los tres artefactos del ciclo SDD: `spec.md -> plan.md -> tasks.md`.

## 2) Alcance

Incluye:

- Sesion persistente de R por `session_id`.
- Herramienta `jmv_ttestIS` con esquema estricto basado en `ttestIS.a.yaml`.
- Motor de traduccion GUI basado en parseo de `*.u.yaml`.
- Mapeo explicito de errores R a codigos JSON-RPC.

No incluye:

- Cobertura completa de todos los modulos `jmv` en esta iteracion.
- UI visual, integraciones web o cambios fuera de MCP server.

## 3) Historias de Usuario Estrictas

US-01  
Como agente IA, debo enviar un array de variables numericas al endpoint `jmv_descriptives` y recibir una tabla JSON plana con media y desviacion estandar, mas una guia textual para replicarlo en menus de jamovi.

US-02  
Como agente IA, debo invocar `jmv_ttestIS` con `deps` y `group` validados contra esquema y obtener resultados serializados sin objetos R6 crudos.

US-03  
Como usuario humano, debo recibir instrucciones GUI con ruta y controles concretos para reproducir manualmente el analisis.

US-04  
Como operador del servidor, debo evitar recargar datasets pesados en cada llamada reutilizando estado de sesion en memoria R.

## 4) Contratos de Interaccion MCP

### 4.1 Entrada comun

- `session_id: string` obligatorio para ejecucion de analisis.
- `analysis_name: string` o endpoint explicito.
- `options: object` validado por Pydantic derivado de `*.a.yaml`.

### 4.2 Salida comun

- `analysis_name: string`
- `session_id: string`
- `tables: Array<Object>` (serializacion tabular plana)
- `markdown: string` (tablas legibles)
- `gui_instructions: string`
- `metadata: object` (flags, truncado, version)

## 5) Requisitos Funcionales

RF-01: El servidor debe cargar datasets a memoria R y devolver `session_id` reutilizable.  
RF-02: El servidor debe rechazar parametros que no cumplan el esquema generado desde `*.a.yaml`.  
RF-03: El servidor debe traducir opciones de analisis a controles GUI via parseo `*.u.yaml`.  
RF-04: El servidor debe convertir resultados R6 a estructuras JSON estables.  
RF-05: El servidor debe mapear errores R relevantes a errores JSON-RPC accionables.

## 6) Requisitos No Funcionales

RNF-01: Ejecucion headless, sin abrir GUI de jamovi.  
RNF-02: Dataset en volumen de solo lectura.  
RNF-03: Latencia reducida por reuso de `session_id` para datasets grandes.  
RNF-04: Trazabilidad: cada respuesta incluye `analysis_name` y `session_id`.

## 7) Mapeo Estatico de Errores (Error Mapping)

| R Exception Pattern | JSON-RPC Code | Message | Suggested Action |
| --- | --- | --- | --- |
| `singular matrix` | `-32602` | Colinealidad extrema detectada. | El agente debe eliminar variables redundantes. |
| `grouping variable must have exactly 2 levels` | `-32602` | Variable de agrupacion invalida para t-test. | Sugerencia: Usar `jmv_anovaOneway`. |
| `missing values in 'x'` | `-32602` | Valores faltantes detectados en variable analizada. | Aplicar filtro NA o exclusion de casos. |
| `not enough observations` | `-32602` | Muestra insuficiente para el analisis solicitado. | Aumentar N o simplificar modelo. |
| no mapeado | `-32000` | Error interno de ejecucion R. | Revisar parametros y reintentar. |

## 8) Criterios de Aceptacion

CA-01: Existe endpoint de carga a memoria que retorna `session_id` valido.  
CA-02: `jmv_ttestIS` falla con error estructurado cuando falta `group` o `deps`.  
CA-03: Respuesta de `jmv_ttestIS` incluye `tables`, `markdown` y `gui_instructions`.  
CA-04: GUI translator obtiene etiquetas de controles desde `*.u.yaml` y no desde mapa hardcodeado.  
CA-05: Al menos 2 errores R del mapa estatico son traducidos con codigo y sugerencia correctos.

## 9) Regla de Ejecucion Iterativa

Por cada nuevo analisis a exponer (`anova`, `regression`, `frequencies`, etc.) se debe crear un subdirectorio nuevo en `.specify/` y repetir el ciclo completo:

1. `spec.md`
2. `plan.md`
3. `tasks.md`

No se autoriza implementacion de codigo antes de cerrar los tres artefactos y su checklist binario.
