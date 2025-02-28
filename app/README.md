# Material Generation API

A Flask-based API server that generates novel materials based on natural language descriptions, using Phi-3-mini for NLP processing and MEGNet+VAE for materials generation.

## Features

- Natural language processing to extract material property constraints
- MEGNet+VAE model for generating materials with desired properties
- CIF structure file generation for 3D visualization
- RESTful API for easy integration with frontend applications

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the application:

Edit `app/config.py` to specify your model paths and configuration settings.

3. Run the server:

```bash
python run.py
```

## API Endpoints

### GET /api/health
Check if the server is running.

### POST /api/generate
Generate materials based on a natural language description.

Request body:
```json
{
  "query": "I need a semiconductor with high mechanical stability",
  "n_samples": 5,
  "temperature": 1.2
}
```

Response:
```json
{
  "success": true,
  "materials": [
    {
      "formula": "LiFePO4",
      "band_gap": 2.1,
      "formation_energy": -1.5,
      "bulk_modulus": 120.5,
      "cif_url": "/api/structures/gen_001_LiFePO4.cif"
    },
    ...
  ]
}
```

### GET /api/structures/{filename}
Get a specific CIF file for a generated material.

## Frontend Integration

This API is designed to work with a Svelte frontend. The API responses include all necessary data for rendering material information and 3D structures.

## License

MIT