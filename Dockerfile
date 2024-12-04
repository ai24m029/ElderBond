# Verwende ein Python-Image als Basis
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere alle Dateien aus deinem aktuellen Verzeichnis in das Container-Verzeichnis /app
COPY . /app

# Installiere die Abhängigkeiten, die in deiner requirements.txt aufgeführt sind
RUN pip install --no-cache-dir -r requirements.txt

# Setze den Befehl, um die Anwendung zu starten (je nach Anwendung anpassen)
#Hier kann auch deine Hauptdatei im Projektverzeichnis sein
CMD ["python", "ElderBond.py"]
