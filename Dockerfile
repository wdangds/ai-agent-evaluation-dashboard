FROM python:3.14.7-slim

WORKDIR /app

# Dependencies first, so Docker caches this layer and rebuilds stay fast
# when only your code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render sets $PORT. Default to 8050 for local runs.
# ENV PORT=8050
# EXPOSE 8050

CMD ["sleep", "infinity"]
