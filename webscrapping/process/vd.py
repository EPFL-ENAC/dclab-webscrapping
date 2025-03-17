"""Processing of data from État de Vaud's Registre du commerce.

Needs Google Maps API key with Geocoding API enabled.
"""

import os

from dotenv import load_dotenv
import pandas as pd
import googlemaps
from ollama import Client

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")


INPUT_PATH = "data/250313_registre commerce vaud_ALL.csv"
ADDRESS_COLUMN_NAME = "Adresse"
POSTAL_CODE_COLUMN_NAME = "NPA"
CITY_COLUMN_NAME = "Localité"
DESCRIPTION_COLUMN_NAME = "Objet"
COMMERCIAL_TYPES = [
    "bakery",
    "bar",
    "beauty_salon",
    "restaurant",
    # Add more types here
    # https://developers.google.com/maps/documentation/places/web-service/supported_types
]

OLLAMA_ATTEMPTS = 5
OLLAMA_MODEL_NAME = "llama3.2:latest"
OLLAMA_SYSTEM_PROMPT = """À partir de la description de commerce donnée, déterminer s'il s'agit d'un commerce officiel ou bien d'une initiative individuelle non-officielle (par exemple à domicile). Ne retourner que un seul mot: "officiel" s'il s'agit d'un commerce officiel, "non-officiel" s'il ne s'agit pas d'un commerce officiel."""


gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
ollama = Client(host=OLLAMA_API_URL)


def get_google_maps_type(address: str) -> list[str]:
    """Get the type of the building at the given address using the Google Maps API.

    Args:
        adress (str): The address of the building.

    Returns:
        list[str]: The types of the building.
    """
    try:
        print(f"Getting building type for {address}")
        geocode_result = gmaps.geocode(address)
        types = geocode_result[0]["types"]
        print(f"For {address}, got types: {types}")
        return types
    except Exception:
        print(f"Could not get building type for {address}")
        return []


def get_google_maps_types(df: pd.DataFrame) -> pd.DataFrame:
    """Get the types of buildings for each address in the DataFrame using the Google Maps API."""

    df = df.copy()
    df["google_maps_building_type"] = df["address_full"].apply(get_google_maps_type)
    df["google_maps_official"] = df["google_maps_building_type"].apply(
        lambda x: any([t in x for t in COMMERCIAL_TYPES])
    )
    return df


def ollama_generate(model: str, instructions: str, prompt: str) -> str:
    """Generate text using the Ollama API."""

    for attempt in range(OLLAMA_ATTEMPTS):
        try:
            response = ""
            stream = ollama.generate(
                model=model,
                system=instructions,
                options={
                    "temperature": 0,
                },
                keep_alive="30m",
                prompt=prompt,
                stream=True,
            )

            for chunk in stream:
                response += chunk.response
                print(chunk.response, end="", flush=True)

            print("")

            return response

        except Exception as e:
            print(f"Attempt {attempt + 1} failed")

    return ""


def get_ollama_type(description: str) -> str:
    """Get the type activity from its description using the Ollama API."""

    try:
        print(f'Getting activity type for "{description}"')
        response = ollama_generate(OLLAMA_MODEL_NAME, OLLAMA_SYSTEM_PROMPT, description)
        return response.lower().strip()
    except Exception:
        print(f'Could not get activity type for "{description}"')
        return ""


def get_ollama_types(df: pd.DataFrame) -> pd.DataFrame:
    """Get the types of buildings for each address in the DataFrame using the Ollama API."""

    df = df.copy()
    df["ollama_activity_type"] = df[DESCRIPTION_COLUMN_NAME].apply(get_ollama_type)
    df["ollama_official"] = df["ollama_activity_type"].apply(lambda x: x == "officiel")
    return df


df = pd.read_csv(INPUT_PATH, sep=";")
df = df.head(20)  # Only keep the first 20 rows for testing purposes
df["address_full"] = df.apply(
    lambda row: f"{row[ADDRESS_COLUMN_NAME]}, {row[POSTAL_CODE_COLUMN_NAME]} {row[CITY_COLUMN_NAME]}",
    axis=1,
)
df = get_google_maps_types(df)
df = get_ollama_types(df)
print(
    df[
        [
            "address_full",
            "google_maps_building_type",
            "google_maps_official",
            "ollama_activity_type",
            "ollama_official",
        ]
    ]
)
