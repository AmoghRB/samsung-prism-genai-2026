# CPU-only image for the MSRIT_Waypoint code-retrieval pipeline.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.hf_cache

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# CPU wheels of torch: no CUDA, ~5x smaller image.
COPY requirements.txt .
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.0 \
 && pip install -r requirements.txt

COPY src/ src/
COPY examples/ examples/

# Bake the model weights into the image so it runs offline.
RUN python -c "from src.retriever import CodeRetriever; CodeRetriever().model"

# Default: reproduce the screening number. Override the command for queries, e.g.
#   docker run --rm -it waypoint python -m src.query --apps -i
CMD ["python", "-m", "src.evaluate"]
