import memory

# Index the documents from the folder
folder_path = "./biblioteca"
memory.index_documents_from_folder(folder_path)

# Get memory snippets for a given user message
user_message = "O que é um elo?"
memory_snippets = memory.get_memory_snippets(user_message, top_n=5)

print(memory_snippets)