from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# PokéAPI base URL
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/"
POKEAPI_SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"

# Function to fetch evolution chain
def get_evolution_chain(pokemon_name):
    try:
        # Fetch Pokémon species data
        species_response = requests.get(f"{POKEAPI_SPECIES_URL}{pokemon_name}")
        if species_response.status_code == 200:
            species_data = species_response.json()
            evolution_chain_url = species_data.get("evolution_chain", {}).get("url")
            if evolution_chain_url:
                # Fetch evolution chain data
                evolution_response = requests.get(evolution_chain_url)
                if evolution_response.status_code == 200:
                    return evolution_response.json()
    except Exception as e:
        print(f"Error fetching evolution chain: {e}")
    return None

# Function to extract evolution chain details
def extract_evolution_chain(chain):
    evolutions = []
    current = chain.get("chain", {})
    while current:
        evolutions.append(current.get("species", {}).get("name"))
        current = current.get("evolves_to", [])[0] if current.get("evolves_to") else None
    return evolutions

@app.route("/", methods=["GET", "POST"])
def index():
    pokemon_data = None
    evolution_chain = None
    error = None

    if request.method == "POST":
        pokemon_name = request.form.get("pokemon_name").strip().lower()
        if pokemon_name:
            try:
                # Fetch Pokémon data
                response = requests.get(f"{POKEAPI_URL}{pokemon_name}")
                if response.status_code == 200:
                    pokemon_data = response.json()
                    # Fetch evolution chain
                    evolution_chain_data = get_evolution_chain(pokemon_name)
                    if evolution_chain_data:
                        evolution_chain = extract_evolution_chain(evolution_chain_data)
                else:
                    error = "Pokémon not found!"
            except Exception as e:
                error = "An error occurred. Please try again."

    return render_template(
        "index.html",
        pokemon_data=pokemon_data,
        evolution_chain=evolution_chain,
        error=error
    )

if __name__ == "__main__":
    app.run(debug=True)