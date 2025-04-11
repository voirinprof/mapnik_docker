FROM ubuntu:20.04

# Désactiver les interactions pendant l'installation
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système, Mapnik et les polices
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    libmapnik-dev \
    python3-mapnik \
    libgdal-dev \
    fonts-dejavu \
    fontconfig \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY requirements.txt .
COPY app.py .
COPY map.xml .
COPY map.xml .

# Installer les dépendances Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Exposer le port Flask
EXPOSE 5000

# Commande pour lancer Flask
CMD ["python3", "app.py"]