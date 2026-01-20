from langgraph.graph import StateGraph, START, END
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import sys
from dotenv import load_dotenv
from typing import TypedDict, List
from langchain_core.documents import Document

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from services.rag_retriever import retrieve_relevant_chunks

# Define the state schema
class GraphState(TypedDict):
    question: str
    chat_history: List[dict]
    retrieved_docs: List[Document]
    answer: str

# LLM Setup
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    temperature=0.0
)

# Prompt Template
prompt_template = PromptTemplate(
    input_variables=["question", "context"],
    template="""
You are a helpful assistant.

Use ONLY the context below to answer the question.

Context:
{context}

Question:
{question}

Answer with short and precise bullet points.
Also provide source citations.
"""
)

# Workflow Graph
graph = StateGraph(GraphState)

def retrieve(state: GraphState) -> GraphState:
    question = state["question"]
    docs = retrieve_relevant_chunks(question)
    state["retrieved_docs"] = docs
    return state

def generate_answer(state: GraphState) -> GraphState:
    context = "\n\n".join([doc.page_content for doc in state["retrieved_docs"]])
    question = state["question"]

    # Format the prompt with the context and question
    formatted_prompt = prompt_template.format(question=question, context=context)
    
    # Use the LLM directly
    answer = llm.invoke(formatted_prompt)

    state["answer"] = answer.content
    return state

# Add nodes to the graph
graph.add_node("retrieve", retrieve)
graph.add_node("generate_answer", generate_answer)

# Set the entry point and add edges
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate_answer")
graph.set_finish_point("generate_answer")

# Compile the graph
graph = graph.compile()
