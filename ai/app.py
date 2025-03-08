import os
import time
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configura tu API Key de OpenAI
OPENAI_API_KEY = "TU_API_KEY_AQUI"
openai.api_key = OPENAI_API_KEY

# Ruta del archivo generado por SUMO
SUMO_FILE_PATH = "/sumo/tripinfo.xml"

def send_to_chatgpt(file_path):
    """Lee el archivo y envía su contenido a ChatGPT para su análisis."""
    try:
        with open(file_path, "r") as file:
            data = file.read()

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en tráfico vehicular."},
                {"role": "user", "content": f"Analiza este archivo XML y dame recomendaciones para mejorar la movilidad:\n\n{data}"}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error al procesar el archivo: {str(e)}"

@app.route("/process", methods=["POST"])
def process_file():
    """Endpoint para que SUMO avise que el archivo está listo."""
    if os.path.exists(SUMO_FILE_PATH):
        analysis = send_to_chatgpt(SUMO_FILE_PATH)
        return jsonify({"message": "Análisis completado", "result": analysis})
    else:
        return jsonify({"error": "El archivo no existe"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
