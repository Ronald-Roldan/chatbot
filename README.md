# Asistente electoral verificable

Prototipo local y gratuito para consultar planes de trabajo electorales del Guayas. Responde solo con evidencia recuperada del corpus y muestra la fuente, página y enlace del PDF.

## Alcance académico

El sistema **no verifica si una propuesta es verdadera ni si será cumplida**. Verifica si una afirmación está respaldada, contradicha o no tiene evidencia suficiente dentro de los documentos incorporados. No representa al CNE.

## Arquitectura

```text
PDF oficial -> extracción/OCR -> fragmentos + metadatos -> PostgreSQL + pgvector
Pregunta -> embeddings locales Ollama -> recuperación híbrida -> respuesta con citas
                                                       -> veredicto de respaldo
```

Todo se ejecuta localmente. No requiere API comercial, cuenta de WhatsApp ni publicar datos a terceros.

## Requisitos

- Docker Desktop
- Python 3.11 o superior
- [Ollama](https://ollama.com/) instalado y ejecutándose
- Para OCR de PDFs escaneados: Tesseract OCR instalado y disponible en `PATH`.

En Windows, instale Docker Desktop, Python y Ollama desde sus sitios oficiales. Después ejecute:

```powershell
ollama pull jina/jina-embeddings-v2-base-es
ollama pull qwen2.5:3b
docker compose up -d
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts\wait_for_db.py
uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000/` para usar el chatbot web o `http://127.0.0.1:8000/docs` para probar la API.

## WhatsApp Cloud API opcional

La tesis exige la integración mediante mensajería. El proyecto incluye el webhook en `/webhook/whatsapp`, pero Meta debe entregar un `PHONE_NUMBER_ID`, token temporal o permanente y token de verificación. Colóquelos en `.env`, exponga temporalmente el servidor HTTPS mediante un túnel seguro para la prueba y registre esa URL como webhook en Meta. La interfaz web local permite evaluar todo el sistema antes de esta integración externa.

## Cargar documentos

1. Descargue únicamente planes de trabajo de fuentes oficiales y guárdelos en `data/raw/`.
2. Cree un registro en `data/metadata/planes.csv` usando `data/metadata/planes.example.csv` como plantilla.
3. Ejecute:

```powershell
python scripts\ingest.py --metadata data\metadata\planes.csv
```

El proceso usa texto embebido en el PDF. Para un PDF escaneado utiliza OCR local si Tesseract está instalado. Revise una muestra de páginas antes de presentar resultados.

## Probar una consulta

```powershell
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question":"¿Qué propone la candidatura sobre seguridad?"}'
```

## Evaluación de tesis

1. Seleccione 50 preguntas realistas y documente cuál es su evidencia esperada.
2. Use `scripts/create_annotation_template.py` para producir pares afirmación-evidencia.
3. Dos anotadores clasifican cada par como `respaldada`, `contradicha` o `insuficiente`.
4. Ejecute `scripts/evaluate_verifier.py` sobre un archivo CSV terminado.
5. Reporte Recall@5, MRR@5, cobertura de citas, F1 macro, matriz de confusión y SUS de usabilidad.

Los formatos, la rúbrica y los protocolos están en `research/`.

## Estructura

- `app/`: API, recuperación, generación y verificación.
- `scripts/`: ingesta, preparación de anotaciones y evaluación.
- `data/`: documentos y metadatos locales; no se versionan PDFs ni información personal.
- `research/`: instrumentos reproducibles para Capítulos III y IV.

## Nota de seguridad y privacidad

No cargue números de teléfono, cédulas, direcciones ni conversaciones identificables. En la evaluación, asigne códigos anónimos a participantes y conserve consentimientos por separado.
