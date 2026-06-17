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
# Note
The model used to generate the tags on my PC is mistral-7b on a GTX 1080.
It's working somewhat fine, but the tags are not very good or concistent. The LLM model is not very good at understanding the titles of the books and following the prompt directions, and it often assigns irrelevant tags. This is something that can be improved in the future by using a different model, or by fine-tuning the prompts used to generate the tags (either by using an overarching system prompt when generating tags, or truly limiting the tags used upon assignment of tags).


