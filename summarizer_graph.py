import streamlit as st
import requests
from pydantic import BaseModel
from typing import Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# --- State schema ---
class SummarizerState(BaseModel):
    url: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None

# Define the state for the workflow
def fetch_website_content(state: SummarizerState) -> SummarizerState:
    url = state.url or ""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        content = f"Error fetching URL: {e}"
    return state.copy(update={"content": content})

def summarize_content(state: SummarizerState) -> SummarizerState:
    content = state.content or ""
    # Placeholder: Replace with your LLM or summarization logic
    summary = content[:500] + "... [truncated]" if len(content) > 500 else content
    return state.copy(update={"summary": summary})

# Build the graph
graph = StateGraph(SummarizerState)
graph.add_node("fetch", fetch_website_content)
graph.add_node("summarize", summarize_content)
graph.add_edge("fetch", "summarize")
graph.add_edge("summarize", END)

graph.set_entry_point("fetch")

# For langgraph dev UI
def get_graph():
    return graph

# --- Streamlit UI ---
st.set_page_config(page_title="Soup Agent - Website Summarizer", page_icon="🦾")
st.title("🦾 Soup Agent: Website Summarizer")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# User input (URL)
user_input = st.chat_input("Paste a website URL to summarize...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.spinner("Summarizing website..."):
        state = SummarizerState(url=user_input)
        result = graph.run(state)
        summary = result.summary
    st.session_state["messages"].append({"role": "assistant", "content": summary})
    st.chat_message("assistant").write(summary)

# For CLI/dev UI usage
def main():
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else input("Enter URL: ")
    state = SummarizerState(url=url)
    result = graph.run(state)
    print("Summary:\n", result.summary)

if __name__ == "__main__":
    main() 