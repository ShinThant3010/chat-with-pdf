# Chat with Multiple Academic PDFs: RAG + Web Search Backend

This project provides an API for question-answering over a set of academic PDFs using Retrieval-Augmented Generation (RAG) and LLMs.  
If the answer can’t be found in your PDFs, it automatically performs web search.  
It supports session-based memory, ambiguous question clarification, and is fully Dockerized.

---

## Features

- **PDF-based RAG QA**: Answers user questions using OpenAI (or other LLM) grounded in ingested PDFs.
- **Web Search Fallback**: If the answer is not in the PDFs, performs real-time web search (Tavily).
- **Clarifier Agent**: Detects ambiguous questions and prompts the user for clarification.
- **Session Memory**: Remembers each user’s chat history for follow-up questions in the same session.
- **Modular Agents**: Clean separation for clarification, PDF RAG, and web search agents.
- **Dockerized**: Easy to run anywhere, with or without Docker Compose.

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/chat-with-pdf.git
cd chat-with-pdf
