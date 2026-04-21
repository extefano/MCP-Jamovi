# Checklist de Cumplimiento Fase 2

## Alcance
Validacion de cumplimiento entre:
- Especificacion Fase 2 ([Especificación de Integración y Traducción.md](Especificación%20de%20Integración%20y%20Traducción.md))
- Implementacion actual del servidor

## Estado global
- Resultado: cumplimiento parcial
- Bloqueadores criticos: gestion de sesion, mapeo de errores, traduccion GUI dinamica, contrato de serializacion extendido

## Revision de nuevas especificaciones
- SPEC-004Expansion del Catalogo Estadistico.md: no implementada en runtime
- SPEC-005 Serializacion de Resultados R6 a JSON-MD.md: implementacion parcial (solo descriptives$asDF)
- SPEC-006 Motor de Traduccion a Instrucciones GUI.md: implementacion parcial (instruccion fija, no motor dinamico)

## Matriz de cumplimiento

1. GUI-TRANS-01
- Estado: parcial
- Evidencia: [src/jamovi_mcp/server.py](../../src/jamovi_mcp/server.py) devuelve gui_instructions fijo para descriptives.
- Gap: no usa archivos .a.yaml/.u.yaml, no hay labels_used ni fallback_used.

2. ERR-MAP-02
- Estado: no cumple
- Evidencia: [src/jamovi_mcp/r_bridge.py](../../src/jamovi_mcp/r_bridge.py) propaga RBridgeError con stderr crudo.
- Gap: no existe esquema MCP de error con code/type/message/suggested_action.

3. DATA-SER-03
- Estado: parcial
- Evidencia: [src/jamovi_mcp/r_bridge.py](../../src/jamovi_mcp/r_bridge.py) extrae result$descriptives$asDF.
- Gap: no serializa title/id/footnotes/truncated/original_size_bytes; no aplica limite de 2 MB.

4. SESS-MAN-01
- Estado: no cumple
- Evidencia: [src/jamovi_mcp/r_bridge.py](../../src/jamovi_mcp/r_bridge.py) recarga dataset en cada llamada.
- Gap: no existe session_id, mcp_active_data persistente ni mcp_last_analysis reutilizable.

5. META-VAL-01
- Estado: parcial
- Evidencia: [src/jamovi_mcp/models.py](../../src/jamovi_mcp/models.py) valida esquema de entrada con Pydantic.
- Gap: no hay pre-flight estadistico (niveles, varianza, tipos jamovi, ID blocking).

6. TOOL-TTEST-01
- Estado: no cumple
- Evidencia: [src/jamovi_mcp/server.py](../../src/jamovi_mcp/server.py) solo publica tool_get_dataset_info y tool_run_descriptives.
- Gap: falta herramienta de t-test independiente y defaults de opciones.

7. ENV-SPEC-04
- Estado: parcial
- Evidencia: [Dockerfile](../../Dockerfile) instala R y paquetes criticos; define /data.
- Gap: no hay enforcement de truncamiento JSON en runtime.

## Matriz por SPEC nueva

1. SPEC-004 Expansion del Catalogo Estadistico
- Estado: no cumple
- Cobertura actual: solo [tool_run_descriptives](../../src/jamovi_mcp/server.py).
- Requerido por spec: jmv_ttestIS y jmv_corrMatrix con validaciones de esquema y columnas.
- Gap critico: no existen modelos Pydantic para estas herramientas ni validacion de group con 2 niveles.

2. SPEC-005 Serializacion R6 a JSON/Markdown
- Estado: parcial
- Cobertura actual: extraccion puntual de [result$descriptives$asDF](../../src/jamovi_mcp/r_bridge.py).
- Requerido por spec: iterar res$items, extraer tablas/notas, producir JSON estructurado y bloque Markdown.
- Gap critico: no existe serializador generico ni traduccion de errores por palabras clave.

3. SPEC-006 Motor de Traduccion GUI
- Estado: parcial
- Cobertura actual: texto fijo gui_instructions en [server.py](../../src/jamovi_mcp/server.py).
- Requerido por spec: servicio GUITranslator con static mapping por tool, menu_path, param_map y texto dinamico.
- Gap critico: no existe modulo de traduccion ni contrato de salida dinamico por parametros.

## Orden recomendado de implementacion
1. SPEC-005 primero: crear serializador robusto y mapper de errores para estabilizar salidas.
2. SPEC-004 segundo: agregar herramientas ttestIS y corrMatrix reutilizando serializador/errores.
3. SPEC-006 tercero: agregar GUITranslator y conectar salida dinamica en cada tool.

## Criterio de cierre sugerido para este bloque
- Se ejecuta descriptives, ttestIS y corrMatrix devolviendo JSON estable + gui_instructions dinamico.
- Los errores de validacion de factor, varianza y NA devuelven codigo/mensaje accionable.
- Toda salida tabular respeta el contrato de serializacion con metadatos y truncamiento.

## Acciones recomendadas para cerrar Fase 2
1. Implementar modulo session_manager con cache por session_id y fingerprint de dataset.
2. Implementar modulo error_mapper con codigos -32001/-32002/-32003.
3. Implementar modulo result_serializer con limite 2 MB y metadatos de tabla.
4. Implementar modulo gui_translator con resolucion de labels y fallback.
5. Agregar tool_run_ttest_independent con pre-flight de niveles y varianza.
6. Agregar pruebas unitarias de contratos de error, truncamiento y validacion previa.
