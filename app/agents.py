from llama_index.llms.openai import OpenAI
from app.pdf_ingest import PDFIngestor
import os
import requests

from dotenv import load_dotenv
load_dotenv()
os.environ.get("TAVILY_API_KEY")

OPENAI_MODEL = "gpt-3.5-turbo"  # or 4o

# 1. Clarifier Agent
def is_ambiguous(question: str) -> bool:
    llm = OpenAI(model=OPENAI_MODEL)
    prompt = (
        "Is the following user question ambiguous or underspecified—meaning it lacks enough detail to answer directly, or could refer to multiple possible things?\n\n"
        "- Answer 'yes' if the question is vague, incomplete, or lacks necessary context (e.g., 'What about the results?', 'Which one is better?', 'How did it perform?').\n"
        "- Answer 'no' if the question is specific and asks for information that could be answered directly from a research paper or document. "
        "Examples of specific questions include: "
        "'Summarize the experimental setup described in the paper.', "
        "'What accuracy was reported for the main model?', "
        "'Which datasets were used for evaluation?', "
        "'List the main contributions stated by the authors.', "
        "'What were the limitations discussed in the study?'.\n\n"
        "Only reply with 'yes' or 'no'.\n\n"
        f"User question: {question}\n"
    )
    response = llm.complete(prompt)
    # LlamaIndex returns a CompletionResponse object; extract .text
    answer = response.text.strip().lower()
    return 'yes' in answer


# 2. PDF Agent (RAG)
def pdf_agent(pdf_ingestor: PDFIngestor, question: str):
    return pdf_ingestor.query(question)

# 3. Web Search Agent (Mock or real API)
def web_search_agent(question: str):
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "[Web search API key not set.]"
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": question,
        "search_depth": "basic",
        "include_answer": True,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Tavily's "answer" field is typically a one-sentence summary, or use top result
        answer = data.get("answer") or (
            data.get("results", [{}])[0].get("content", "[No web answer found.]")
        )
        return answer
    except Exception as e:
        return f"[Web search failed: {e}]"

# 4. Router Agent (history-aware)
def router_agent_with_history(pdf_ingestor, question, history):
    # Concatenate previous Q&A as context for the retriever/LLM
    if history:
        context = ""
        for turn in history[-3:]:  # Use last 3 turns (you can adjust)
            context += f"User: {turn['question']}\nAssistant: {turn['answer']}\n"
        question_for_rag = f"{context}User: {question}"
    else:
        question_for_rag = question

    print('question for rag: ', question_for_rag)
    # (pass question_for_rag for history-aware RAG, question for simple RAG)
    if is_ambiguous(question_for_rag):
        return("Your question is a bit vague. Can you clarify what you mean?","clarifier")
    chunks = pdf_ingestor.retrieve_chunks(question_for_rag, top_k=3)
    if not chunks or all(len(c.strip()) < 30 for c in chunks):
        web_answer = web_search_agent(question_for_rag)
        return (web_answer, "web")
    rag_answer = pdf_ingestor.query(question_for_rag)
    return (rag_answer, "pdf")

# 4. Router Agent (simple)
def router_agent(pdf_ingestor: PDFIngestor, question: str):
    if is_ambiguous(question):
        return ("Your question is a bit vague. Can you clarify what you mean?", "clarifier")

    # Step 1: Try strict PDF retrieval
    chunks = pdf_ingestor.retrieve_chunks(question, top_k=3)
    # print(chunks)
    if not chunks or all(len(c.strip()) < 30 for c in chunks): 
        web_answer = web_search_agent(question)
        return (web_answer, "web")

    # Step 2: Synthesize answer using RAG
    rag_answer = pdf_ingestor.query(question)
    return (rag_answer, "pdf")
