# This utility is used to assign tags to all publications in the Thorium database. It uses a local LLM (using Ollama API to access it) based on the title of each publication.
# Requires the following things to be set up:
# 1. A local LLM model running on Ollama (https://ollama.com/)
# 2. A Thorium database with publications that need to be tagged.
# 3. The Ollama API client library installed in the Python environment (can be installed using pip install ollama).
    # To create a venv in the project directory, run the following command in the terminal:
    # python -m venv venv
    # To activate the venv, run the following command in the terminal:
    # On Linux: source venv/bin/activate
    # To install the Ollama API client library, run the following command in the terminal:
    # pip install ollama
# 4. The location of the Thorium database (simple JSON file). The path to the database should be the following by defaults: ~/.config/EDRLab.ThoriumReader/config-data-json/state.json
    # This json file has no whitespace, but here's how the structure looks like:
    # {
    #     "publication": {
    #         "db": {
    #             "id_of_book1": {
    #                 "title": "title of book 1",
    #                 "tags": ["tag1", "tag2"]
    #             },
    #             "id_of_book2": {
    #                 ...
    #             }
    #         }
    #    }
    # }
# 5. Thorium must be closed before running this utility, as it will overwrite the state.json file.
import json
import ollama

MODEL_NAME = "mistral"  # Replace with your actual model name
NUMBER_OF_TAGS = 50  # Maximum number of tags to generate
NUMBER_OF_TAGS_PER_PUBLICATION = 10  # Maximum number of tags to assign to each publication
DATABASE_PATH = "/home/knorax/.config/EDRLab.ThoriumReader/config-data-json/state.json"

def get_all_publications(database_path):
    with open(database_path, 'r') as f:
        data = json.load(f)
    return data['publication']['db']

# This function first gives the LLM the title of all publications and asks it to generate a list of all unique tags that could be relevant for these publications. This can help in creating a comprehensive list of tags that can be used for tagging the publications later on.
def generate_list_of_tags_from_all_books(publications):
    titles = [publication_data.get("title", "") for publication_id, publication_data in publications.items()]
    prompt = f'''Given the following list of publication titles: {titles}, generate a comprehensive list of unique tags that could be relevant for these publications. Provide the tags as a comma-separated list. Each tag should have an upper case letter at the start of each word and the rest of the word should be lower caps. If a tag contains multiple words, they should be space separated. For example, if the title is "The Great Gatsby", a relevant tag could be "Classic Literature". Only provide the tags without any additional text. Try to limit the number of word per tag to a maximum of 3 words. Start with signle word tags and then move to multiple word tags if it's absolutely necessary. Do not repeat tags that mean the same thing. For example, if you have the tag "Sci-Fi", do not also generate the tag "Science Fiction". Limit the number of tags to a maximum of {NUMBER_OF_TAGS}. Do not use author names as tags. You can use genre names as tags. Focus on themes, topics, and other relevant aspects of the publications that can help in categorizing them effectively. Do not cheat by combining tags in a single word. For example, if you need to add the tags "Box Making", do not combine the words into a single tag "BoxMaking". Do not include bash command or common function names as tags. For example, do not include the tag "ls" or "cd" or "mkdir" or "rm" or "touch" or "echo" or "cat" or "grep" or "find" or "awk" or "sed" or "tar" or "zip" or "unzip" or "curl" or "wget". Do not include book titles as tags. For example, do not include the tag "To Kill a Mockingbird" or "1984". Do not include song titles as tags. For example, do not include the tag ""Bohemian Rhapsody"" or ""Stairway to Heaven"".'''
    schema = {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["tags"]
    }
    
    response = ollama.chat(
        model=MODEL_NAME,  # Replace with your actual model name
            messages=[{"role": "user", "content": prompt}],
            format=schema
    )

    return json.loads(response["message"]["content"])

def assign_tags_to_publication(publication_title, tag_list=None):
    print(f"Assigning tags for publication: '{publication_title}'")
    # This function uses the Ollama API to get tags for a publication based on its title.
    # The prompt is designed to ask the LLM to generate relevant tags for the publication.
    prompt = f'''Given the following tag list '{tag_list}', assign relevant tags for a publication with the title: '{publication_title}'. Provide a list of tags separated by commas. Tags must be from the provided tag list. No additional tags should be generated. A limit of 10 tags can be used, no more. Less than {NUMBER_OF_TAGS_PER_PUBLICATION} tags may be used if the publication is not relevant to all tags in the tag list.'''
    schema = {
        "type": "object",
        "properties": {
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["tags"]
    }
    
    # Call the Ollama API to get the tags with the given prompt and schema.
    response = ollama.chat(
        model=MODEL_NAME,  # Replace with your actual model name
            messages=[{"role": "user", "content": prompt}],
            format=schema
    )

    return json.loads(response["message"]["content"])

def assign_tags_to_all_publications(publications, tag_list):
    print("Assigning tags to publications...")
    success_count = 0
    warning_count = 0
    warnings = []
    new_publications = publications.copy()
    for publication_id, publication_data in publications.items():
        title = publication_data.get("title", "")
        if title:
            tags = assign_tags_to_publication(title, tag_list)
            if any(tag not in tag_list for tag in tags):
                warning_count += 1
                warnings.append(f"Tag '{tags}' generated for publication '{title}' is not in the original tag list.")
                print(f"\033[33m[WARNING]\033[0m Tag '{tags}' generated for publication '{title}' is not in the original tag list.")
                break
            else:
                success_count += 1
                print(f"\033[32m[SUCCESS]\033[0m")
                new_publications[publication_id]["tags"] = tags["tags"]
            print(f"Publication ID: {publication_id}, Title: {title}, Tags: {tags}")

    print(f"Tag assignment completed. {success_count} tags assigned successfully, {warning_count} warnings.")
    print(f"\033[33m[WARNINGS]\033[0m {warnings}")
    print(f"\033[33m[WARNINGS END]\033[0m")

    return new_publications

def update_database(database_path, publications):
    with open(database_path, 'r') as f:
        data = json.load(f)

    data['publication']['db'] = publications

    with open(database_path, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    database_path = DATABASE_PATH
    publications = get_all_publications(database_path)

    tag_list = generate_list_of_tags_from_all_books(publications)
    print(f"Generated Tag List: {tag_list}")
    print("=="*50)

    publications = assign_tags_to_all_publications(publications, tag_list)
    print(f"Updated Publications with Tags: {publications}")

    with open("updated_publications.json", 'w') as f:
        json.dump({"publication": {"db": publications}}, f, indent=4)

    update_database(database_path, publications)

if __name__ == "__main__":
    main()
