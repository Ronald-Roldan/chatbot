# Borrador para Capítulo III Metodología

## Tipo y diseño de investigación

La investigación es aplicada porque desarrolla y evalúa un prototipo tecnológico para facilitar la consulta documentada de planes de trabajo electorales. Se emplea un diseño de desarrollo tecnológico con evaluación cuantitativa del desempeño de recuperación, respaldo documental y usabilidad.

## Población y muestra documental

La población está conformada por los planes de trabajo de candidaturas de la provincia del Guayas publicados por fuentes oficiales para el período electoral seleccionado. La muestra será no probabilística e intencional, integrada por los documentos que cumplan los criterios de disponibilidad pública, procedencia oficial, legibilidad y metadatos verificables. Cada documento conservará su URL, fecha de descarga y suma SHA-256 para asegurar trazabilidad.

## Desarrollo del prototipo

Los documentos PDF se procesan mediante extracción directa de texto y, cuando sea necesario, OCR local. El texto se normaliza y se divide en fragmentos aproximados de 420 palabras con solapamiento de 80 palabras. Cada fragmento conserva la página de inicio y fin, además de sus metadatos electorales. Los fragmentos se representan mediante embeddings locales y se almacenan en PostgreSQL con pgvector. Ante una consulta, el sistema combina similitud semántica y búsqueda léxica, recupera los cinco fragmentos de mayor puntuación y genera una respuesta restringida a esta evidencia. La interfaz devuelve las citas documentales y un veredicto de respaldo.

## Variables e indicadores

| Variable | Indicador | Medición |
|---|---|---|
| Recuperación documental | Recall@5 y MRR@5 | Conjunto de consultas con página esperada |
| Respaldo documental | Accuracy, precisión, recall y F1 macro | Pares afirmación-evidencia adjudicados |
| Trazabilidad | Cobertura de citas | Respuestas con fuente y página verificables |
| Usabilidad | Puntaje SUS | Encuesta posterior a tareas guiadas |

## Consideraciones éticas

El prototipo utiliza documentos de carácter público provenientes de fuentes oficiales. No recolecta datos personales innecesarios. Las personas participantes se identifican con códigos y reciben información previa sobre el propósito académico del estudio. El sistema no determina la veracidad de propuestas ni predice resultados electorales; solamente indica el grado de respaldo de una respuesta respecto del corpus incorporado.
