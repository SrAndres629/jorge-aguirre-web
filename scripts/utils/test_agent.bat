@echo off
echo 🤖 Entrando al cerebro de Antigravity (Qwen 2.5 Coder)...
docker exec -it antigravity_brain aider --model ollama/qwen2.5-coder:7b --map-tokens 1024
pause
