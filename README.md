# Web scrapping


## Installation

In a virtual environment (not mandatory but recommended), install the required packages:
```bash
git clone https://github.com/EPFL-ENAC/dclab-webscrapping.git
cd dclab-webscrapping
pip install -e .
```


## Processing État de Vaud's "Registre du commerce"

Script: `./webscrapping/process/vd.py`

Create a `.env` file with the following content:
```
GOOGLE_MAPS_API_KEY="..."
OLLAMA_API_URL="..."
```

You may install Ollama locally to use a LLM on your local machine. In this case, the `OLLAMA_API_URL` should look like `http://localhost:11434`.


## Scrapping Instagram

Script: `./webscrapping/scrap/instagram.py`

Create a `.env` file with the following content:
```
INSTAGRAM_USERNAME="..."
INSTAGRAM_PASSWORD="..."
```
