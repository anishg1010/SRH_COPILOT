# SRH AI Copilot

SRH AI Copilot is a modular university AI assistant platform.  
The first implemented domain agent is **LINC**, the Learning and Innovation Agent, designed to support lecturers with competence-oriented course design, learning objectives, teaching methods, assessments, rubrics, and responsible AI integration.

## Project Goal

This project is not about training a new large language model.  
It is about building a reliable AI-assisted system using:

- Open-source local LLMs through Ollama
- Internal university documents
- Metadata-driven document ingestion
- Chunking and multilingual embeddings
- A shared RAG pipeline
- Domain-specific agents
- A scalable orchestration layer

## High-Level Architecture

```text
User Chat UI
   ↓
Core Orchestrator
   ↓
Router
   ↓
Domain Agent
   ↓
Shared RAG Pipeline
   ↓
Vector Database
   ↓
Ollama LLM
   ↓
Structured Answer with Sources
```

## Current Scope

The first prototype focuses on:

```text
Lecturers → LINC Agent → Internal LINC Documents → RAG → Ollama Response
```

Future agents can be added without rewriting the shared pipeline:

- Career Support Agent
- HR Agent
- Student Services Agent
- Strategic Intelligence Agent

## Folder Structure

```text
SRH_AI_COPILOT/
├── agents/
│   ├── linc/
│   ├── career_support/
│   └── future_agent_template/
├── core/
├── ingestion/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── metadata/
│   └── vector_db/
├── frontend/
├── evaluation/
├── config/
├── logs/
├── notebooks/
├── scripts/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── main.py
```

## Data Design

Raw documents are organized by:

1. Agent/domain
2. Category
3. Language

Example:

```text
data/raw/linc/core_principles/english/
data/raw/linc/policies/german/
data/raw/linc/responsible_ai/mixed/
```

The machine retrieval logic should rely on metadata, not only folders.

## Metadata Levels

### Document Metadata

Created once per document.

```json
{
  "document_id": "linc_core_principles_001",
  "agent": "linc",
  "department": "learning_and_innovation",
  "category": "core_principles",
  "document_type": "guideline",
  "language": "en",
  "source_file": "core_principles.pdf",
  "status": "approved",
  "access_level": "lecturer"
}
```

### Chunk Metadata

Created for every chunk stored in the vector database.

```json
{
  "chunk_id": "linc_core_principles_001_chunk_003",
  "document_id": "linc_core_principles_001",
  "agent": "linc",
  "category": "core_principles",
  "topic": "competence_oriented_learning",
  "page": 4,
  "language": "en",
  "source_file": "core_principles.pdf"
}
```

## Setup

### 1. Create virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Ollama

Install Ollama from the official Ollama website, then pull a local model:

```bash
ollama pull llama3.1:8b
```

Optional smaller/faster model:

```bash
ollama pull qwen2.5:7b
```

### 4. Configure environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### 5. Run the application skeleton

```bash
python main.py
```

## Development Phases

### Phase 1: Folder structure and metadata schema

- Create project structure
- Define category schema
- Define agent registry
- Prepare document registry

### Phase 2: Ingestion pipeline

- Extract text
- Detect language
- Classify document
- Create metadata
- Clean text
- Chunk documents
- Save `documents.jsonl` and `chunks.jsonl`

### Phase 3: Vector database

- Generate multilingual embeddings
- Store chunks in ChromaDB
- Test retrieval quality

### Phase 4: LINC Agent

- Route lecturer query to LINC
- Retrieve internal context
- Generate answer with Ollama
- Show source references

### Phase 5: Chatbot UI

- Build basic Streamlit app
- Show answer and retrieved sources
- Add feedback logging

## Recommended Models

```yaml
LLM:
  provider: ollama
  model: llama3.1:8b

Embeddings:
  provider: sentence_transformers
  model: intfloat/multilingual-e5-small
```

## Git Guidelines

Do not commit:

- `.env`
- `venv/`
- vector database files
- raw confidential university documents
- generated logs
- cache folders

Commit:

- source code
- schemas
- configs
- example metadata
- documentation
- tests

## Team Collaboration

Each team member can work on one agent while sharing the same core system.

```text
Anish → LINC Agent
Keyur → Career Support Agent
Atharv → HR Agent
Yuvraj → Student Services Agent
Mohit → Core Orchestrator
```

The shared files are:

```text
core/
ingestion/
config/
data/metadata/
```

Work carefully here because changes affect all agents.
