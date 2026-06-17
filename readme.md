# Description
This project is a simple implementation of a tool to apply tags to publications inside the Thorium E-book reader. The tags are based on the title of each books, and assigned by a local LLM model.

# Usage
1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. Make sure Ollama LLM model is running:
   ```bash
   ollama serve
   ```
3. Run the script to apply tags to publications:
   ```bash
   python main.py
   ```

