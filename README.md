# Mapnik with Docker Compose

This repository provides a `docker-compose` setup to run a server based on Mapnik. It includes Mapnik for map rendering, a Flask server to serve a raster (map), and a ready-to-use environment with custom fonts.

## Prerequisites

- Docker and Docker Compose installed on your system.
- A shapefile (e.g., `world.shp`) placed in a `data/` directory for geographic data.

## Project Structure

```
mapnik_docker/
├── data/              # Directory for shapefiles 
├── mapnik/            # Directory containing the Mapnik service configuration
│   ├── Dockerfile     # Docker image definition
│   ├── app.py         # Flask application to serve tiles
│   ├── map.xml        # Mapnik style for rendering maps
│   └── requirements.txt  # Python dependencies
├── docker-compose.yml # Docker Compose configuration
└── README.md          # This file
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/mapnik_docker.git
   cd mapnik_docker
   ```

2. **Place your data**:
   - Copy your shapefile (e.g., `world.shp`) into the `data/` directory.

3. **Create your map.xml**:
   - Create your map.xml into the `mapnik/` directory.
   - This file will have the definition of the map (layer, style,...)

4. **Build and start the services**:
   ```bash
   docker-compose up --build -d
   ```
   - The `--build` flag forces rebuilding the image if needed.
   - `-d` runs the containers in detached mode.

## Usage

- Once the containers are running, access the Flask API to generate a map:
  ```
  http://localhost:5000/map_from_xml
  ```
  or
  ```
  http://localhost:5000/map_from_python
  ```
  
  This returns a PNG image rendered by Mapnik using the shapefile data. You could change the code in app.py

- To stop the services:
  ```bash
  docker-compose down
  ```


## Customization
- **Mapnik Styles**: Edit `map.xml` to adjust rendering styles (colors, fonts, etc.).
- **Data**: Replace `world.shp` with your own shapefiles in `data/`.
- **Fonts**: DejaVu fonts are included. Add other fonts via the `Dockerfile` (e.g., `fonts-roboto`).

It is better to use a XML to set a map (https://get-map.org/mapnik-lost-manual/book.html)

## Contributing
Contributions are welcome! Open an issue or submit a pull request on GitHub.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.