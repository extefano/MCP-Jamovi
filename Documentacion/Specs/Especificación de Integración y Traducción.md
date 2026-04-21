# Especificacion de Diseno Detallado: Fase 2

## Modulo
Integracion R-MCP y Motor de Traduccion GUI Dinamico

## Estado
Borrador validado para implementacion (SDD) - v2.1

## Referencia
Complementa:
- SPEC-001 (Requisitos iniciales)
- SPEC-002 (Diseno tecnico)

## 1. Objetivo
Definir contratos de comunicacion, serializacion y persistencia para que el servidor MCP:
- Ejecute analisis en R de forma segura.
- Traduzca resultados tecnicos a pasos reproducibles en la GUI de jamovi.
- Mantenga estado de sesion para consultas incrementales.
- Devuelva errores deterministas y accionables para el agente.

## 2. Decisiones de arquitectura para Fase 2

### 2.1 Transporte MCP
- Modo obligatorio en Fase 2 local: stdio.
- Modo opcional futuro: SSE, sin alterar contratos JSON definidos aqui.

### 2.2 Entorno y aislamiento
- El dataset debe resolverse dentro del volumen interno /data.
- Rutas absolutas del host deben rechazarse.
- El volumen /data se considera de solo lectura.

### 2.3 Integracion R
- Se permite rpy2 o subprocess con Rscript.
- Queda prohibido eval(parse(text=...)).

## 3. Motor de traduccion GUI dinamico (GUI-TRANS-01)

### 3.1 Fuentes de verdad
- Archivo .a.yaml: nombres internos de opciones.
- Archivo .u.yaml: etiquetas visibles en GUI.

### 3.2 Algoritmo de mapeo
Dado un analisis A y un parametro P:
1. Localizar A.u.yaml.
2. Buscar componente con name == P.
3. Extraer label.
4. Generar instruccion con patron: [Accion] + [Label] + [Valor].

### 3.3 Contrato de salida de traduccion
El nodo gui_recreation_instructions debe incluir:
- menu_path: ruta de navegacion en jamovi.
- steps: arreglo ordenado de pasos textuales.
- labels_used: pares parametro-label resueltos.

### 3.4 Reglas de fallback
Si no se encuentra label en .u.yaml:
- Usar tabla estatica interna de respaldo.
- Marcar fallback_used=true en metadatos de respuesta.

## 4. Capa de gestion de errores (ERR-MAP-02)

### 4.1 Objetivo
Traducir errores cripticos de R a errores MCP estables con mensaje, causa y accion sugerida.

### 4.2 Esquema de error MCP
Toda falla funcional debe serializar como:
- code (int)
- type (string)
- message (string)
- r_pattern (string opcional)
- suggested_action (string)

### 4.3 Matriz minima obligatoria
- Patron: must have exactly 2 levels
  code: -32001
  type: DataError
  message: La variable de agrupacion requiere exactamente 2 niveles para un T-Test.
  suggested_action: Usa ANOVA para mas de 2 niveles.

- Patron: cannot be constant
  code: -32002
  type: VarianceError
  message: La variable seleccionada no tiene varianza.
  suggested_action: Selecciona otra variable dependiente o filtra correctamente.

- Patron: missing values in 'x'
  code: -32003
  type: MissingDataError
  message: Se detectaron valores perdidos en la variable analizada.
  suggested_action: Filtra NA o cambia la politica de exclusion de casos.

## 5. Serializacion de resultados R6 y tablas (DATA-SER-03)

### 5.1 Regla de extraccion
- No se permite serializacion profunda de objetos R6.
- Solo deben extraerse nodos de tabla con propiedad o metodo asDF.

### 5.2 Contrato de tabla serializada
Cada tabla debe incluir:
- id: identificador tecnico de la tabla.
- title: titulo legible.
- content: arreglo JSON por filas.
- footnotes: arreglo de notas.
- truncated: booleano.
- original_size_bytes: entero.

### 5.3 Limite de tamano
- MEM_LIMIT_TABLE_JSON_BYTES = 2097152 (2 MB).
- Si se supera el limite:
  - aplicar truncamiento por filas,
  - establecer truncated=true,
  - adjuntar warning en metadatos.

## 6. Gestor de sesion R con estado (SESS-MAN-01)

### 6.1 Contrato de sesion
El estado minimo debe conservar:
- session_id
- active_dataset_path
- active_dataset_fingerprint
- last_analysis_name
- last_analysis_result_ref
- updated_at

### 6.2 Ciclo de vida del dataset
- Carga condicional: read_omv() solo si cambia dataset_path o fingerprint.
- Puntero activo en R: mcp_active_data.
- Ultimo resultado en R: mcp_last_analysis.

### 6.3 Limpieza y reinicio
- Prohibido rm(list=ls()) durante operacion normal.
- En reinicio: limpieza selectiva de objetos temporales.
- Las sesiones inactivas deben expirar por timeout configurable.

## 7. Validacion de metadatos y tipos (META-VAL-01)

### 7.1 Atributos minimos a validar
- measureType
- dataType
- levels (si aplica)
- unique_count
- variance (en variables numericas)

### 7.2 Reglas por tipo jamovi
- ID:
  - Bloquear en analisis inferenciales.
  - Permitir en inspeccion descriptiva basica.

- Nominal/Ordinal:
  - Debe exponer levels.
  - En ttestIS, group debe tener exactamente 2 niveles.

- Continuous:
  - Requerida como dependiente en ttestIS.
  - Debe tener varianza mayor a 0.

### 7.3 Pre-flight check obligatorio
Antes de llamar jmv::<analisis>:
1. Validar existencia de variables.
2. Validar compatibilidad de tipos.
3. Validar cardinalidad de levels en factores.
4. Validar varianza no nula en dependientes.

## 8. Herramienta t-test independiente (TOOL-TTEST-01)

### 8.1 Parametros requeridos
- dep: variable dependiente continua.
- group: variable de agrupacion nominal/ordinal de 2 niveles.

### 8.2 Opciones por defecto alineadas
- welch=true
- mann=false
- norm=true
- eqv=true

### 8.3 Contrato de respuesta
Debe devolver:
- analysis_results.tables (serializadas segun DATA-SER-03)
- analysis_results.summary
- gui_recreation_instructions
- metadata.validation_report

## 9. Criterios de aceptacion de Fase 2
- El servidor traduce al menos descriptives y ttestIS a pasos GUI con labels reales.
- Los errores de R definidos en ERR-MAP-02 se transforman al esquema MCP.
- La salida de tablas respeta limite de 2 MB con truncamiento explicito.
- El dataset no se recarga si no cambio path/fingerprint.
- Se conserva mcp_last_analysis para consultas de seguimiento.

## 10. Fuera de alcance en Fase 2
- Renderizado de graficos en base64.
- Persistencia en base de datos externa.
- Soporte multitenant distribuido entre multiples procesos.
