# DocIntelli

AI-powered document intelligence platform built with FastAPI, PostgreSQL, PgVector, and NVIDIA NIMs.

DocIntelli enables users to upload documents, perform semantic search, ask context-aware questions, compare documents, and retrieve information through a Retrieval-Augmented Generation (RAG) pipeline.

---

## Features

### Document Upload & Processing

* Upload PDF documents
* Extract document content
* Chunk large documents into manageable sections
* Generate embeddings using NVIDIA NIMs

### Semantic Search

* Store vector embeddings in PostgreSQL using PgVector
* Perform similarity search using cosine distance
* Retrieve the most relevant document chunks

### Conversational Question Answering

* Ask natural language questions about uploaded documents
* Context-aware responses using retrieved document chunks
* Multi-turn conversation support with memory

### Document Comparison

* Compare multiple documents
* Identify similarities and differences
* Generate AI-powered comparison summaries

### Agent-Based Architecture

Current agents:

* Retrieval Agent
* Analysis Agent
* Memory Agent
* Orchestrator Agent

Planned migration:

* Agno Agent Framework
* Agent Teams
* Tool-based Retrieval
* Persistent Agent Memory

---

## Architecture

```text
User Query
    │
    ▼
Orchestrator Agent
    │
    ▼
Analysis Agent
    │
 ┌──┼─────────────┐
 ▼  ▼             ▼
Memory     Retrieval Agent
Agent            │
                 ▼
          Retrieval Service
                 │
                 ▼
             PgVector
                 │
                 ▼
          Relevant Chunks
                 │
                 ▼
            NVIDIA NIM
                 │
                 ▼
          Final Response
```

---

## Tech Stack

### Backend

* FastAPI
* SQLModel
* PostgreSQL
* PgVector

### AI & Machine Learning

* NVIDIA NIMs
* OpenAI Compatible SDK
* Embedding Models
* Large Language Models

### Infrastructure

* Docker
* Docker Compose
* UV Package Manager

---

## Project Structure

```text
Document_Intelligence/
│
├── agents/
│   ├── analysis_agent.py
│   ├── memory_agent.py
│   ├── orchestrator_agent.py
│   ├── retrieval_agent.py
│   └── tools.py
│
├── core/
├── models/
├── routers/
├── schemas/
├── services/
│   ├── embedding_service.py
│   ├── retrieval_service.py
│   └── llm_service.py
│
├── storage/
├── main.py
├── docker-compose.yml
└── Dockerfile
```

---

## Retrieval-Augmented Generation (RAG) Flow

### Document Ingestion

1. Upload PDF
2. Extract text
3. Chunk document
4. Generate embeddings
5. Store embeddings in PgVector

### Query Flow

1. User submits question
2. Generate query embedding
3. Search PgVector
4. Retrieve top relevant chunks
5. Build context
6. Send context to NVIDIA LLM
7. Generate answer

---

## Local Development

### Clone Repository

```bash
git clone https://github.com/lahineers/Document-Intelligence-Enhanced-.git
cd Document-Intelligence-Enhanced-
```

### Create Environment

```bash
uv venv
source .venv/bin/activate
```

### Install Dependencies

```bash
uv sync
```

### Configure Environment

Create:

```bash
.env
```

Example:

```env
NVIDIA_API_KEY=your_api_key

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/docintelli

LLM_MODEL=your_llm_model
EMBEDDING_MODEL=your_embedding_model
```

### Run Application

```bash
uv run python main.py
```

or

```bash
uvicorn main:app --reload
```

---

## Future Roadmap

* Hybrid Search
* Reranking
* Document Summarization
* Cross-Document Intelligence
* Streaming Responses
* Production Monitoring
* Evaluation Framework
* Enterprise Authentication

---

## Author

**Sreenihal Premjith**

Document Intelligence & Agentic AI Engineering
