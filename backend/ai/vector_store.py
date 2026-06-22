from dotenv import load_dotenv
load_dotenv()

# pyrefly: ignore [missing-import]
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import FAISS

from ai.context_builder import build_context


def build_vector_store(transactions):

    documents = build_context(transactions)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001"
    )

    vector_store = FAISS.from_texts(
        documents,
        embedding=embeddings
    )

    return vector_store