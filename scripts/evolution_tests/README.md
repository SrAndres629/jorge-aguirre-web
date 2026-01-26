# 🧪 Evolution API Testing Suite

Esta carpeta contiene herramientas de nivel ingeniería para depurar y certificar la integración con Evolution API y n8n sin depender exclusivamente de dispositivos físicos.

## 📁 Componentes

### 1. `webhook_listener.py`
Un servidor FastAPI que escucha eventos entrantes. 
- **Uso**: Úsalo para ver exactamente qué envía la API.
- **Ejecución**: `python scripts/evolution_tests/webhook_listener.py`
- **Puerto**: 8081 (por defecto).

### 2. `event_simulator.py`
Un generador de eventos sintéticos.
- **Uso**: Envía "fakes" al listener para probar tu lógica de procesamiento, estados de conexión o detección de palabras clave en el chatbot.
- **Ejecución**: `python scripts/evolution_tests/event_simulator.py`

## 🛠️ Flujo de Prueba Senior

1.  Inicia el **Listener** en una terminal.
2.  En otra terminal, corre el **Simulator**.
3.  Observa cómo el Listener recibe y formatea el JSON.
4.  Una vez validado el formato, puedes cambiar la URL en el simulador hacia tu instancia de **n8n** para probar el flujo completo sin enviar un mensaje real por WhatsApp.

---
*Jorge Aguirre Flores Web Project - Backend Automation Division*
