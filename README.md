RAG App for DOTA 2 Patch Notes
==============================

### Overview

This demo project showcases how Retrieval-Augmented Generation (RAG) can deliver accurate and source-grounded responses by leveraging Large Language Models (LLMs) alongside domain-specific knowledge repositories.
Designed as a demo app focused on DOTA 2 Patch Notes, it allows users to query updates related to heroes, items, and abilities across different patches with high precision. The app addresses the challenge of AI hallucinations by integrating LangChain, FAISS, and OpenAI to dynamically retrieve only the most relevant information.
Instead of relying on web URLs as input sources, this project uses JSONLoader to process pre-downloaded and structured JSON files, ensuring faster and more consistent access to patch data.

---

### Sample Queries
![image](https://github.com/user-attachments/assets/034c22eb-bf9b-4d8d-839d-909de1b32b04)

### Project Highlights

#### **Core Technologies**
- **LangChain** - Framework for building applications powered by LLMs.
- **OpenAI** - Main provider for LLMs used.
- **FAISS** - Vector store for storing and retrieving document embeddings.
- **LangGraph** - Ensures flexible, multi-turn conversation flows and complex query handling.
- **Gradio** - Simple and interactive web UI for user interaction.
- **PowerShell Scripts** - Automated patch fetching, preprocessing, and vector store updates.

#### **Key Features**
1. **RAG Workflow** - Combines GPT's natural language capabilities with accurate document retrieval.
2. **Multi-Turn Context Awareness** - Allows follow-up queries like *"How about Medusa?"* without losing context.
3. **Dynamic Filtering** - Categorizes data based on heroes, abilities, items, and patches.
4. **Patch Update Automation** - Automatically fetches and processes the latest patches from the DOTA 2 API.
5. **Interactive UI** - Gradio-based interface with buttons for clearing memory and real-time updates.
6. **Robust Error Handling** - Displays process status and errors during initialization and updates.

#### **Main Components**
- **app.py** - Launches the Gradio interface and handles user queries.
- **chain_builder.py** - Constructs the RAG pipeline using LangChain.
- **strainer.py** - Filters retrieved documents based on metadata.
- **storer.py** - Manages storage and data processing tasks.
- **download_patch_notes.py** - Fetches raw patch notes from the DOTA 2 API.
- **fetch_mappers.py** - Downloads and preprocesses hero, item, and ability mappings.
- **modify_patch_notes.py** - Cleans and modifies patch notes for better retrieval performance.
- **add_to_vectorstore.py** - Updates FAISS vector store with new data.

#### **Automation Scripts**
- **start.ps1** - Powershell script that automates patch updates and launches the app.

---

### **Prerequisites**
- OpenAI account
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

### Credits
- **OpenAI** for GPT models.
- **LangChain** for simplifying AI workflows.
- **Gradio** for the user interface.
- **FAISS** for fast vector search.
- **DOTA 2 API** for patch data.

---

