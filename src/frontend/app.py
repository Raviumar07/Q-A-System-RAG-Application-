import streamlit as st
import requests
import json

# Backend API configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Document Q&A Assistant",
    layout="wide"
)

st.title("📄 Document Q&A Assistant")
st.write(
    "Upload PDFs or provide website URLs and ask questions based on your documents."
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False


st.sidebar.header("📥 Upload Knowledge Source")

uploaded_files=st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.sidebar.button("Process PDF Files"):
        with st.sidebar.spinner("Processing PDF files..."):
            try:
                # Prepare files for upload
                files = []
                for uploaded_file in uploaded_files:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    files.append(("files", (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")))
                
                # Send to backend
                response = requests.post(f"{API_BASE_URL}/upload/pdf", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.document_uploaded = True
                    st.sidebar.success(f"✅ Processed {len(uploaded_files)} PDF(s) - {result.get('total_chunks', 0)} chunks created")
                else:
                    st.sidebar.error(f"❌ Error processing PDFs: {response.text}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    else:
        st.sidebar.info(f"📄 {len(uploaded_files)} file(s) ready to process")


url=st.sidebar.text_input("Or enter a website URL")

if st.sidebar.button("Add URL"):
    if url:
        with st.sidebar.spinner("Processing website..."):
            try:
                # Send URL to backend
                response = requests.post(
                    f"{API_BASE_URL}/upload/url", 
                    json={"url": url}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.document_uploaded = True
                    st.sidebar.success(f"✅ Processed URL - {result.get('total_chunks', 0)} chunks created")
                else:
                    st.sidebar.error(f"❌ Error processing URL: {response.text}")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    else:
        st.sidebar.warning("Please enter a valid URL.")


st.subheader("💬 Ask Questions")

# Disable chat if no documents uploaded
if not st.session_state.document_uploaded:
    st.info("Please upload a PDF or ingest a website before asking questions.")

for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(message["content"])


user_question = st.chat_input(
    "Ask a question about your documents...",
    disabled=not st.session_state.document_uploaded
)

# Reset button
if st.button("🔄 Reset Chat & Documents"):
    try:
        # Reset backend
        response = requests.post(f"{API_BASE_URL}/reset")
        if response.status_code == 200:
            # Reset frontend state
            st.session_state.chat_history = []
            st.session_state.document_uploaded = False
            st.success("✅ Reset complete!")
            st.rerun()
        else:
            st.error(f"❌ Error resetting: {response.text}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")      



if user_question:
    # Store user message
    st.session_state.chat_history.append(
        {"role": "user", "content": user_question}
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_question)

    # Get AI response from backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/query",
                    json={
                        "question": user_question,
                        "chat_history": st.session_state.chat_history
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get("answer", "No answer generated")
                    sources = result.get("sources", [])
                    source_details = result.get("source_details", [])
                    total_chunks = result.get("total_chunks_retrieved", len(sources))
                    
                    # Display the answer
                    st.markdown(ai_response)
                    
                    # Display sources if available
                    if sources:
                        # Get unique sources
                        unique_sources = list(set([s for s in sources if s]))
                        
                        if len(unique_sources) == 1:
                            st.markdown(f"**Source:** {unique_sources[0]}")
                            st.caption(f"📄 Answer based on {total_chunks} relevant chunks from this document")
                        else:
                            st.markdown("**Sources:**")
                            for i, source in enumerate(unique_sources, 1):
                                st.markdown(f"{i}. {source}")
                            st.caption(f"📄 Answer based on {total_chunks} chunks from {len(unique_sources)} documents")
                        
                        # Show expandable source details
                        with st.expander("� View Source Details", expanded=False):
                            for i, detail in enumerate(source_details, 1):
                                st.markdown(f"**{i}. {detail.get('chunk_info', f'Chunk {i}')}**")
                                st.markdown(f"*Source: {detail.get('source', 'Unknown')}*")
                                st.code(detail.get('preview', 'No preview available'), language=None)
                                if i < len(source_details):
                                    st.divider()
                else:
                    ai_response = f"❌ Error getting response: {response.text}"
                    st.markdown(ai_response)
                    
            except Exception as e:
                ai_response = f"❌ Connection error: {str(e)}"
                st.markdown(ai_response)

    # Store AI response
    st.session_state.chat_history.append(
        {"role": "assistant", "content": ai_response}
    )
