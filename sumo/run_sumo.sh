#!/bin/bash

# Definir las rutas de los archivos
CONFIG_FILE="./config.sumocfg"
OUTPUT_FILE="./tripinfo.xml"
AI_API_URL="http://ai:5000/process"  # Endpoint de la IA en Docker

echo "📂 Buscando archivo en: $CONFIG_FILE"
ls -l "$CONFIG_FILE"


# Verificar si el archivo de configuración existe
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: No se encontró el archivo de configuración en $CONFIG_FILE"
    exit 1
fi

echo "🚦 Ejecutando SUMO..."
sumo -c "$CONFIG_FILE" --tripinfo-output "$OUTPUT_FILE"

# Esperar a que el archivo se genere
while [ ! -f "$OUTPUT_FILE" ]; do
    sleep 1
done

# Verificar si el archivo de salida fue generado
if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Simulación completada. Archivo generado en: $OUTPUT_FILE"
    
    # Enviar el archivo a la IA
    echo "📡 Enviando archivo a la IA para análisis..."
    RESPONSE=$(curl -X POST "$AI_API_URL" -H "Content-Type: application/json" -d '{}')

    echo "📊 Respuesta de la IA: $RESPONSE"
else
    echo "❌ Error: No se generó el archivo de salida."
fi
