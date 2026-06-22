from dotenv import load_dotenv
load_dotenv()

# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI
from ai.vector_store import build_vector_store
from ai.prompts import SYSTEM_PROMPT

def ask_question(question: str, transactions) -> dict:
    """
    Builds the vector store from transactions, retrieves relevant documents
    based on the user's question, formats the system prompt with context,
    queries the Gemini model, and returns the grounded answer.
    """
    if not transactions:
        return {"answer": "No financial records found in the database. I cannot answer questions without data."}

    # 1. Build the vector store from current transactions
    vector_store = build_vector_store(transactions)

    # 2. Retrieve relevant transactions.
    # Since the dataset is small, retrieve up to 15 transactions to ensure adequate coverage of context.
    k = min(15, len(transactions))
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)

    # 3. Format context
    context = "\n\n".join([doc.page_content for doc in docs])

    # 4. Initialize the Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

    # 5. Format prompt and request answer
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nContext:\n{context}"},
        {"role": "user", "content": question}
    ]

    try:
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        answer = f"Error generating answer: {e}"

    return {
        "answer": answer
    }
