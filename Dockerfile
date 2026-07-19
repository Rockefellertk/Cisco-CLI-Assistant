FROM python:3.12-slim

WORKDIR /app

# System deps kept minimal on purpose (pure-Python stack, no compiled deps)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Regenerate the JSON database at build time so it's always in sync with
# database/generate_db.py (safe/no-op if you commit commands.json directly).
RUN python database/generate_db.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "app.bot"]
