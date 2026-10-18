# Protocolo de evaluación del asistente electoral

## Objetivo

Evaluar la recuperación de evidencia, el respaldo documental de las respuestas y la usabilidad del prototipo para consultas sobre planes de trabajo electorales del Guayas.

## Diseño

Estudio aplicado, cuantitativo con apoyo descriptivo. La unidad de análisis es una consulta y la respuesta generada por el prototipo. El corpus se limita a planes de trabajo oficiales incluidos en `planes.csv`.

## Muestra documental

Registre para cada PDF: URL oficial, fecha de descarga, SHA-256, elección, dignidad, cantón, candidatura y organización política. Excluya documentos inaccesibles, duplicados o sin fuente oficial. Declare el número final de documentos, páginas y fragmentos.

## Preguntas de recuperación

Prepare como mínimo 50 preguntas antes de medir. Para cada una, indique el documento y la página de evidencia esperada. Distribuya las preguntas por dignidad, cantón y tema. No cambie las respuestas esperadas después de observar el resultado sin registrar la modificación.

Calcule:

- Recall@5: proporción de consultas cuya evidencia esperada aparece en los cinco primeros fragmentos.
- MRR@5: promedio de `1/rango` de la primera evidencia correcta; cero si no aparece entre los cinco primeros.
- Cobertura de citas: respuestas con al menos una cita verificable divididas para el total de respuestas.

## Anotación de respaldo

Dos anotadores trabajan de forma independiente sobre pares `afirmación–evidencia`.

| Etiqueta | Criterio |
|---|---|
| respaldada | La evidencia expresa directamente la afirmación o permite inferirla sin agregar información nueva. |
| contradicha | La evidencia niega explícitamente la afirmación o presenta un hecho incompatible. |
| insuficiente | La evidencia no permite confirmar ni negar la afirmación. |

Antes de anotar, ambos clasifican 30 pares piloto y discuten únicamente la rúbrica. Luego etiquetan el conjunto principal. Un tercer criterio o acuerdo documentado resuelve desacuerdos. Reporte porcentaje de acuerdo y Cohen kappa antes de adjudicar.

## Usabilidad

Reclute 10–20 participantes mayores de edad. Presente una pantalla de información y consentimiento; asigne un código como P01 y no almacene nombre, teléfono ni cédula junto con la encuesta. Pida tres tareas: localizar una propuesta, comprobar su fuente y reconocer un caso sin evidencia. Después aplique SUS y una pregunta abierta.

## Amenazas a la validez

- El corpus puede no representar todas las candidaturas o planes.
- Errores del OCR pueden afectar recuperación y citas.
- Los resultados describen este corpus, modelos y equipo de evaluación; no prueban cumplimiento futuro de propuestas.
- Un LLM local puede producir salidas variables; fije modelo, versión, temperatura 0 y fecha de ejecución.
