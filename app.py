import os
import uuid
import logging
import streamlit as st
from src.graph import MixRAGGraph
from src.document_processor import DocumentProcessor
from src.document_splitter import DocumentSplitter
from src.document_retriever import DocumentRetriever
from src.config import ConfigManager
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv, find_dotenv

import os

# Force Streamlit to use the repo's .streamlit directory instead of root "/"
os.environ["STREAMLIT_CONFIG_DIR"] = os.path.join(os.path.dirname(__file__), ".streamlit")

load_dotenv(find_dotenv())

# -------------------------
# Helper functions
# -------------------------
def convert_history_to_lc_messages(history):
    lc_messages = []
    for m in history:
        if m['role'] == 'user':
            lc_messages.append(HumanMessage(content=m['content']))
        elif m['role'] == 'assistant':
            lc_messages.append(AIMessage(content=m['content']))
    return lc_messages

def clean_streamed_text(text):
    """Remove metadata, JSON, and unwanted document content."""
    text = text.strip()
    if not text:
        return ""
    # Skip JSON-looking content
    if text.startswith("{") and text.endswith("}"):
        return ""
    # Skip common doc metadata or email/links
    skip_keywords = [
        "binary_score", "email", "linkedin", "github", "website", 
        "experience", "education •", "•", "http://", "https://"
    ]
    if any(keyword in text.lower() for keyword in skip_keywords):
        return ""
    return text

# -------------------------
# Load config and logger
# -------------------------
try:
    config = ConfigManager()._config
    logging.basicConfig(
        level=getattr(logging, config['app']['log_level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
except Exception as e:
    st.error(f"❌ Configuration Error: {str(e)}")
    st.error("🔑 Please set the OPENAI_API_KEY environment variable")
    st.error("💡 Create a .env file with: OPENAI_API_KEY=your_key_here")
    st.stop()

# -------------------------
# Streamlit app
# -------------------------
st.set_page_config(page_title="MixRAG Demo", layout="wide")
st.title("🤖 MixRAG Document + URL QA with Memory")

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = str(uuid.uuid4())

if 'knowledge_base_built' not in st.session_state:
    st.session_state['knowledge_base_built'] = False

if 'current_sources' not in st.session_state:
    st.session_state['current_sources'] = []

if 'document_retriever' not in st.session_state:
    st.session_state['document_retriever'] = None

# Display chat history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

tab1, tab2, tab3 = st.tabs(["💬 Chat","🔄 Workflow Graph", "📊 Analytics"])

# -------------------------
# Chat Tab
# -------------------------
with tab1:
    # File uploader
    uploaded_files = st.sidebar.file_uploader(
        "Upload files (PDF, DOCX, TXT)",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt']
    )
    
    # URLs input
    urls = st.sidebar.text_area("Paste web URLs (comma separated)", height=100, placeholder="https://example1.com, https://example2.com, https://example3.com")

    # Collect sources from uploaded files and URLs
    sources = []
    
    # Process uploaded files - extract file paths
    if uploaded_files:
        for f in uploaded_files:
            sources.append({
                "type": "file",
                "name": f.name,
                "content": f.getvalue()  # this gives bytes
            })
        # for f in uploaded_files:
        #     # Get the file path from the uploaded file object
        #     file_path = f.name
        #     if hasattr(f, 'file') and hasattr(f.file, 'name'):
        #         file_path = f.file.name
        #     elif hasattr(f, '_file') and hasattr(f._file, 'name'):
        #         file_path = f._file.name
        #     elif hasattr(f, 'path'):
        #         file_path = f.path
            
        #     # If we can't get the actual path, use the filename
        #     if not file_path or file_path == f.name:
        #         file_path = f.name
            
        #     sources.append(file_path)
        #     st.sidebar.info(f"Added file: {file_path}")
    


    # Process URLs
    if urls:
        for url in urls.split(','):
            url = url.strip()
            if url:
                sources.append(url)

    # Check if sources have changed
    sources_changed = False
    if sources != st.session_state['current_sources']:
        sources_changed = True
        st.session_state['knowledge_base_built'] = False
        st.session_state['document_retriever'] = None

    # Build Knowledge Base Button
    col1, col2 = st.columns([1, 3])
    with col1:
        build_kb_button = st.button("🔨 Build Knowledge Base", type="primary")
    
    with col2:
        if st.session_state['knowledge_base_built']:
            st.success("✅ Knowledge base is ready!")
        elif sources:
            st.warning("⚠️ Please build knowledge base before asking questions")
        else:
            st.info("📚 Add files or URLs to build knowledge base")

    # Build knowledge base when button is clicked or sources changed
    if build_kb_button and sources:
        with st.spinner("🔨 Building knowledge base..."):
            try:
                # Document processing
                document_processor = DocumentProcessor()
                docs_list = document_processor.load_documents(sources)
                
                if not docs_list:
                    st.error("❌ No documents loaded! Please check your files and URLs.")
                    st.stop()
                
                document_splitter = DocumentSplitter()
                doc_splits = document_splitter.split_documents(docs_list)
                logger.info(f"Split documents into {len(doc_splits)} chunks")
                
                document_retriever = DocumentRetriever(doc_splits)
                
                # Store in session state
                st.session_state['document_retriever'] = document_retriever
                st.session_state['current_sources'] = sources.copy()
                st.session_state['knowledge_base_built'] = True
                
                st.success(f"✅ Knowledge base built successfully! Loaded {len(docs_list)} documents, created {len(doc_splits)} chunks.")
                
            except Exception as e:
                st.error(f"❌ Error building knowledge base: {str(e)}")
                logger.error(f"Knowledge base build error: {e}")

    # Only allow questions if knowledge base is built
    if not st.session_state['knowledge_base_built']:
        st.info("💡 Upload files/URLs and click 'Build Knowledge Base' to start asking questions")
        st.stop()

    user_input = st.chat_input("Type your question here...")

    if user_input:
        # Use the pre-built document retriever from session state
        document_retriever = st.session_state['document_retriever']
        top_docs = document_retriever.retrieve_top_k(user_input, k=3)
        retrieved_docs = document_retriever.retrieve_documents(user_input, k=3)

        # Sidebar: show retrieved docs
        with st.sidebar.expander("📚 Retrieved Documents", expanded=False):
            for i, d in enumerate(top_docs, 1):
                with st.expander(f"Document {i}: {d.metadata.get('source','Unknown')}", expanded=False):
                    st.markdown(f"**Source:** {d.metadata.get('source','Unknown')}")
                    if 'page' in d.metadata:
                        st.markdown(f"**Page:** {d.metadata.get('page','N/A')}")
                    st.markdown(f"**Content:** ```{d.page_content[:200]}{'...' if len(d.page_content) > 200 else ''}```")

        # Initialize Agentic RAG Graph
        chatbot = MixRAGGraph(document_retriever.retriever_tool)

        # -------------------------
        # Add user message
        # -------------------------
        st.session_state['message_history'].append({'role': 'user', 'content': user_input})
        with st.chat_message("user"):
            st.text(user_input)

        # -------------------------
        # Stream Agentic RAG response
        # -------------------------
        history_msgs = convert_history_to_lc_messages(st.session_state['message_history'])

        with st.chat_message("assistant"):
            response_container = st.empty()
            final_response = ""
            
            try:
                for message_chunk, metadata in chatbot.workflow.stream(
                    {"messages": history_msgs},
                    config={"configurable": {"thread_id": st.session_state['thread_id']}},
                    stream_mode="messages"
                ):
                    # Log node execution
                    if hasattr(metadata, 'get') and metadata.get('node'):
                        debug_nodes.write(f"🔄 Executing node: {metadata['node']}")
                    
                    if not hasattr(message_chunk, "content"):
                        continue
                    
                    # Clean the text to remove JSON artifacts
                    clean_text = clean_streamed_text(message_chunk.content)
                    if not clean_text:
                        continue
                    
                    final_response += clean_text + " "
                    response_container.markdown(final_response.strip())
            except Exception as e:
                logger.error(f"Agentic RAG workflow error: {e}")
                
                # Fallback to simple RAG if Agentic RAG fails
                if retrieved_docs:
                    context = "\n\n".join([doc.page_content for doc in retrieved_docs[:3]])
                    fallback_prompt = f"Based on the following context, answer this question: {user_input}\n\nContext:\n{context}"
                    
                    try:
                        model = init_chat_model(
                            config['model_config']['response_model'], 
                            temperature=config['model_config']['temperature']
                        )
                        fallback_response = model.invoke([{"role": "user", "content": fallback_prompt}])
                        final_response = fallback_response.content
                        response_container.markdown(final_response)
                    except Exception as fallback_error:
                        final_response = f"Sorry, I encountered an error while processing your question: {str(e)}"
                        response_container.markdown(final_response)
                else:
                    final_response = "I couldn't find any relevant information to answer your question."
                    response_container.markdown(final_response)

        st.session_state['message_history'].append({'role': 'assistant', 'content': final_response.strip()})

# -------------------------
# Graph Tab
# -------------------------
with tab2:
    st.subheader("🔄 RAG Workflow Architecture")
    
    # Create the DOT graph string
    dot_graph = """
    digraph G {
        rankdir=TB;
        size="12,8";
        node [shape=box, style="filled,rounded", fontname="Arial", fontsize="12"];
        
        // Nodes
        user [label="👤 User Query", fillcolor="#e3f2fd", color="#1976d2", fontcolor="#1976d2"];
        generate [label="🤖 Generate Query\\nor Respond", fillcolor="#e8f5e8", color="#388e3c", fontcolor="#388e3c"];
        retrieve [label="🔍 Retrieve\\nDocuments", fillcolor="#fff3e0", color="#f57c00", fontcolor="#f57c00"];
        rewrite [label="✏️ Rewrite\\nQuestion", fillcolor="#fce4ec", color="#c2185b", fontcolor="#c2185b"];
        answer [label="💬 Generate\\nAnswer", fillcolor="#f3e5f5", color="#7b1fa2", fontcolor="#7b1fa2"];
        grade [label="📊 Grade\\nDocuments", fillcolor="#e0f2f1", color="#00796b", fontcolor="#00796b"];
        
        // Edges
        user -> generate [label="Input Query"];
        generate -> retrieve [label="Need Documents?"];
        retrieve -> grade [label="Retrieved Chunks"];
        grade -> rewrite [label="Relevant?"];
        rewrite -> answer [label="Refined Query"];
        answer -> user [label="Final Response"];
        generate -> answer [label="Direct Answer", style=dashed, color="#666666"];
        grade -> answer [label="Highly Relevant", style=dashed, color="#666666"];
    }
    """
    
    # Display the graph using st.graphviz_chart
    st.graphviz_chart(dot_graph, use_container_width=True)

# -------------------------
# Analytics Tab
# -------------------------
with tab3:
    st.subheader("📊 Analytics Dashboard")
    
    # Conversation Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Messages", len(st.session_state['message_history']))
    with col2:
        user_msgs = len([m for m in st.session_state['message_history'] if m['role'] == 'user'])
        st.metric("User Questions", user_msgs)
    with col3:
        ai_msgs = len([m for m in st.session_state['message_history'] if m['role'] == 'assistant'])
        st.metric("AI Responses", ai_msgs)
    
    # Message Length Analysis
    if st.session_state['message_history']:
        st.subheader("📏 Message Length Analysis")
        user_lengths = [len(m['content']) for m in st.session_state['message_history'] if m['role'] == 'user']
        ai_lengths = [len(m['content']) for m in st.session_state['message_history'] if m['role'] == 'assistant']
        
        col1, col2 = st.columns(2)
        with col1:
            if user_lengths:
                st.metric("Avg User Question Length", f"{sum(user_lengths)/len(user_lengths):.0f} chars")
                st.metric("Longest Question", f"{max(user_lengths)} chars")
        with col2:
            if ai_lengths:
                st.metric("Avg AI Response Length", f"{sum(ai_lengths)/len(ai_lengths):.0f} chars")
                st.metric("Longest Response", f"{max(ai_lengths)} chars")
    
    # Source Information
    st.subheader("📚 Source Information")
    if st.session_state['current_sources']:
        file_count = len([s for s in st.session_state['current_sources'] if isinstance(s, dict)])
        url_count = len([s for s in st.session_state['current_sources'] if isinstance(s, str) and (s.startswith("http://") or s.startswith("https://"))])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Files Uploaded", file_count)
        with col2:
            st.metric("URLs Added", url_count)
        
        # Show knowledge base status
        st.subheader("🔨 Knowledge Base Status")
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state['knowledge_base_built']:
                st.success("✅ Built")
            else:
                st.error("❌ Not Built")
        with col2:
            if st.session_state['document_retriever']:
                st.metric("Document Chunks", "Available")
            else:
                st.metric("Document Chunks", "None")
    
    # Recent Activity
    st.subheader("🕒 Recent Activity")
    if st.session_state['message_history']:
        recent_msgs = st.session_state['message_history'][-5:]  # Last 5 messages
        for msg in recent_msgs:
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            st.text(f"{role_icon} {msg['role'].title()}: {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}")
    
    # Performance Metrics
    st.subheader("⚡ Performance Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Session Duration", "Active")
        st.metric("Thread ID", st.session_state['thread_id'][:8] + "...")
    with col2:
        st.metric("Memory Usage", "Session-based")
        st.metric("Response Quality", "RAG-powered")
