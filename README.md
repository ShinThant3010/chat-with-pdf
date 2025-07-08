# Chat with Multiple Academic PDFs: RAG + Web Search Backend

This project provides an API for question-answering over a set of academic PDFs using Retrieval-Augmented Generation (RAG) and LLMs.
If the answer can’t be found in your PDFs, it automatically performs web search.
It supports session-based memory, ambiguous question clarification, and is fully Dockerized.

---

## Features

- **PDF-based RAG QA**: Answer user questions using OpenAI grounded in ingested PDFs.
- **Web Search Fallback**: If the answer is not in the PDFs, perform real-time web search (Tavily).
- **Clarifier Agent**: Detect ambiguous questions and prompts the user for clarification.
- **Session Memory**: Remember each user’s chat history for follow-up questions in the same session.
- **Modular Agents**: Clean separation for clarification, PDF RAG, and web search agents.
- **Dockerized**: Easy to run anywhere, with or without Docker Compose.

---

## Quick Start

### 1. Clone the Repository

    git clone https://github.com/ShinThant3010/chat-with-pdf.git
    cd chat-with-pdf

### 2. Add Your API Keys

Copy `.env.example` to `.env` and fill in your keys:
```
OPENAI_API_KEY=sk-xxx
TAVILY_API_KEY=tvly-xxx
```


### 3. Place Your PDFs

Put your PDF files in the `papers/` directory.

### 4. Run the App

**With Docker (Recommended):**

    docker-compose up --build

**Or Locally:**

    pip install -r requirements.txt
    uvicorn app.main:app --reload

### 5. Test the API

- Open http://localhost:8000/docs for the Swagger UI.

## API Endpoints

- **POST `/ask`**
  - Input: `{ "session_id": "user1", "question": "your question here" }`
  - Output:
    ```json
    {
      "answer": "text",
      "agent": "pdf", // or "web" or "clarifier"
      "session_id": "user1",
      "history": [ /* ...previous Q&A objects... */ ]
    }
    ```
- **POST `/clear`**
  - Input: `{ "session_id": "user1" }`
  - Output: `{ "message": "Session user1 memory cleared." }`

---

## How It Works

1. **Clarifier**:
   If the user’s question is ambiguous, the clarifier agent prompts for clarification.

2. **PDF Retrieval**:
   For clear questions, it uses RAG to find the answer in your PDFs.

3. **Web Search**:
   If no strong answer is found in the PDFs, it queries the web (Tavily).

4. **Session Memory**:
   Each user session (`session_id`) maintains its own history, which can be used for follow-up questions and context.

---

## Evaluation & Testing

- Add test questions in `golden_qa.json`.
- Run `evaluate.py` to check the system against gold answers, agents, and optionally see retrieval confidence scores.

---

## Project Structure

<pre> <code> ``` 
    chat-with-pdf/ 
    │ 
    ├── app/ 
    │ ├── main.py 
    │ ├── agents.py 
    │ ├── pdf_ingest.py 
    │ └── ... (other modules) 
    ├── sample_papers/                 # Put your PDFs here 
    ├── Dockerfile 
    ├── docker-compose.yml 
    ├── requirements.txt 
    ├── README.md 
    ├── .env                           # Your API keys (not committed) 
    ├── .env.example 
    ├── golden_qa.json                 # Evaluation gold questions 
    ├── evaluate.py                    # Automated evaluation script 
    ``` </code> </pre>

---

## Customization & Extension Ideas

- **Smarter Paper Routing**:
  Add logic to direct questions to the correct PDF based on keywords or entities.
- **Citations**:
  Return source text and paper title with every answer.
- **Session Storage**:
  Use Redis or a database instead of in-memory dict for scale.
- **LangGraph**:
  For advanced agent orchestration and multi-agent workflows.
- **UI Frontend**:
  Build a simple web frontend to interact with the API.

---

## Caveats & Tips

- In-memory session storage is **not persistent**; restart clears memory.
- Ensure you have enough OpenAI/Tavily quota for large experiments.
- To add more PDFs, just drop them into `sample_papers/` and restart the app.

---

## Acknowledgments

- [LlamaIndex](https://llamaindex.ai/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tavily Web Search API](https://www.tavily.com/)
- [OpenAI](https://platform.openai.com/)

---

Questions?
Feel free to open an issue or reach out to the project maintainer.
