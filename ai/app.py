import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Volvemos a usar localhost ya que estaremos en la red del host
LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"

# Ruta del archivo generado por SUMO
SUMO_FILE_PATH = "/sumo/tripinfo.xml"

def send_to_lmstudio(file_path):
    """Lee el archivo XML y lo envía a LM Studio para análisis."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
        
        payload = {
            "model": "deepseek-chat",  # Asegúrate de que el modelo esté disponible en LM Studio
            "messages": [
                {"role": "system", "content": "Eres un experto en tráfico vehicular."},
                {"role": "user", "content": f"Analiza este archivo XML y dame recomendaciones para mejorar la movilidad:\n\n{data}"}
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"Intentando conectar a LM Studio en: {LMSTUDIO_API_URL}")
        
        # Intenta conectar a LM Studio con un timeout más largo
        response = requests.post(LMSTUDIO_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        
        return response_json.get("choices", [{}])[0].get("message", {}).get("content", "No se recibió respuesta")
    except requests.exceptions.RequestException as e:
        return f"Error de conexión con LM Studio: {str(e)}"
    except Exception as e:
        return f"Error al procesar el archivo: {str(e)}"

@app.route("/")
def home():
    """Ruta principal para verificar que el servicio está corriendo."""
    return jsonify({"message": "Servicio SUMO-AI activo"}), 200

@app.route("/check-lmstudio")
def check_lmstudio():
    """Endpoint para verificar la conexión con LM Studio."""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            return jsonify({"status": "LM Studio conectado correctamente", "models": response.json()})
        else:
            return jsonify({"status": "Error", "message": f"LM Studio respondió con código {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route("/process", methods=["POST"])
def process_file():
    """Endpoint para que SUMO avise que el archivo está listo."""
    if os.path.exists(SUMO_FILE_PATH):
        analysis = send_to_lmstudio(SUMO_FILE_PATH)
        return jsonify({"message": "Análisis completado", "result": analysis})
    else:
        return jsonify({"error": f"El archivo no existe en la ruta: {SUMO_FILE_PATH}"}), 400

if __name__ == "__main__":
    # Si usamos network_mode: "host", no podemos usar 0.0.0.0 o el contenedor
    # intentará usar todas las interfaces de red disponibles
    app.run(port=5000)