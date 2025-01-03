RAG App for DOTA 2 Patch Notes
==============================

## Overview
This project demonstrates how **Retrieval-Augmented Generation (RAG)** can provide more **accurate, source-grounded answers** by combining **Large Language Models (LLMs)** with domain-specific knowledge bases.
The demo app focuses on **DOTA 2 Patch Notes**, enabling users to query updates about heroes, items, and abilities from different patches with precision. It addresses the problem of AI **hallucinations** by integrating **LangChain**, **FAISS**, and **OpenAI** to dynamically retrieve relevant information.

---

## Sample Queries

![image](https://github.com/user-attachments/assets/034c22eb-bf9b-4d8d-839d-909de1b32b04)

- *"What changes did Axe get in the latest patch?"*
- *"How about Medusa?"*
- *"Summarize item changes in 7.37e."*

---

## Project Highlights

### **Core Technologies**
- **LangChain** - Framework for building applications powered by LLMs.
- **OpenAI GPT-4o** - Provides the AI capabilities for natural language understanding.
- **FAISS** - Fast and scalable vector store for storing and retrieving document embeddings.
- **LangGraph** - Ensures flexible, multi-turn conversation flows and complex query handling.
- **Gradio** - Simple and interactive web UI for user interaction.
- **PowerShell Scripts** - Automated patch fetching, preprocessing, and vector store updates.

### **Key Features**
1. **RAG Workflow** - Combines GPT's natural language capabilities with accurate document retrieval.
2. **Multi-Turn Context Awareness** - Allows follow-up queries like *"How about Medusa?"* without losing context.
3. **Dynamic Filtering** - Categorizes data based on heroes, abilities, items, and patches.
4. **Patch Update Automation** - Automatically fetches and processes the latest patches from the DOTA 2 API.
5. **Interactive UI** - Gradio-based interface with buttons for clearing memory and real-time updates.
6. **Robust Error Handling** - Displays process status and errors during initialization and updates.

---

## Folder Structure
```
├── data
│   ├── mappers
│   │   ├── heroes_mapper.csv
│   │   ├── items_mapper.csv
│   │   ├── heroes_abilities_mapper.csv
│   │   └── list_patchnotes.csv
├── patchnotes_modified
├── src
│   ├── api
│   │   └── app.py
│   ├── init_setup
│   │   ├── download_patch_notes.py
│   │   ├── fetch_mappers.py
│   │   └── modify_patch_notes.py
│   ├── utils
│   │   ├── chain_builder.py
│   │   ├── strainer.py
│   │   └── storer.py
│   ├── vectorstore
│   │   └── add_to_vectorstore.py
├── vectorstore_faiss
├── start.ps1
├── requirements.txt
└── README.md
```

---

## Files Overview

### **Main Components**
- **app.py** - Launches the Gradio interface and handles user queries.
- **chain_builder.py** - Constructs the RAG pipeline using LangChain.
- **strainer.py** - Filters retrieved documents based on metadata.
- **storer.py** - Manages storage and data processing tasks.
- **download_patch_notes.py** - Fetches raw patch notes from the DOTA 2 API.
- **fetch_mappers.py** - Downloads and preprocesses hero, item, and ability mappings.
- **modify_patch_notes.py** - Cleans and modifies patch notes for better retrieval performance.
- **add_to_vectorstore.py** - Updates FAISS vector store with new data.

### **Automation Scripts**
- **start.ps1** - Powershell script that automates patch updates and launches the app.

---

## Setup and Execution

### **Prerequisites**
- Python 3.10 or later
- Create a virtual environment:
  ```bash
  python -m venv myenv
  source myenv/bin/activate    # Linux/MacOS
  myenv\Scripts\activate       # Windows
  ```

- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### **Launching the App**
1. Open PowerShell and run the following command:
   ```powershell
   ./start.ps1
   ```
2. The app will automatically:
   - Check for the latest patch.
   - Update local data if a new patch is detected.
   - Launch the Gradio interface.
3. Access the app via the local URL displayed in the terminal.

---

## Use Cases
- **E-Sports Analysts** - Quickly review hero changes across patches.
- **DOTA 2 Enthusiasts** - Explore historical patch updates without manually browsing patch notes.
- **Developers** - Learn how to integrate RAG pipelines with custom datasets.
- **AI Researchers** - Demonstrate solutions for AI hallucinations and accuracy challenges.

---

## Limitations
- **Patch Dependency** - Requires manual updates to mappings if patch note structures change significantly.
- **Limited Context Window** - Cannot handle very large patch notes in a single query.
- **Experimental** - Built as a demo app to explore RAG patterns and may require further optimizations.

---

## Future Enhancements
- **Pagination Support** - Improve UI to handle larger result sets.
- **Fine-Tuned Models** - Explore fine-tuning OpenAI models for specific domains.
- **Multi-Language Support** - Add translations for non-English queries.
- **GraphRAG Integration** - Experiment with graph databases for deeper query understanding.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Credits
- **OpenAI** for GPT models.
- **LangChain** for simplifying AI workflows.
- **Gradio** for the user interface.
- **FAISS** for fast vector search.
- **DOTA 2 API** for patch data.

---

Let me know if you'd like any adjustments!

