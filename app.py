"""Streamlit Web Application for Study Assistant."""

import os
from pathlib import Path
import streamlit as st

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.generator import generate_answer
from src.pdf_loader import load_pdf
from src.pipeline import RAGPipeline

st.set_page_config(
    page_title="Study Assistant",
    page_icon="📚",
    layout="wide",
)

# Initialize Session State
if "pipeline" not in st.session_state:
    st.session_state["pipeline"] = RAGPipeline()

if "indexed_chunks" not in st.session_state:
    st.session_state["indexed_chunks"] = 0

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

pipeline: RAGPipeline = st.session_state["pipeline"]

# ==========================================
# SIDEBAR: Document Ingestion & Management
# ==========================================
with st.sidebar:
    st.title("📚 Study Assistant")
    st.markdown("Upload course notes, syllabi, or research papers in PDF format.")

    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or more PDF files to index into the knowledge base.",
    )

    col1, col2 = st.columns(2)
    with col1:
        index_clicked = st.button("Index documents", use_container_width=True, type="primary")
    with col2:
        clear_clicked = st.button("Clear index", use_container_width=True)

    if index_clicked:
        if not uploaded_files:
            st.warning("Please select at least one PDF file to index.")
        else:
            with st.spinner("Extracting text, chunking, and embedding documents..."):
                total_added = 0
                errors: list[str] = []

                for uploaded_file in uploaded_files:
                    try:
                        # Ingest the uploaded file buffer
                        added = pipeline.ingest([uploaded_file])
                        total_added += added
                    except ValueError as e:
                        errors.append(str(e))
                    except Exception as e:
                        errors.append(f"Unexpected error processing '{uploaded_file.name}': {e}")

                st.session_state["indexed_chunks"] = pipeline.store.total_chunks

                if total_added > 0:
                    st.success(f"Successfully indexed {total_added} chunk(s) across {len(uploaded_files)} file(s).")

                for err in errors:
                    st.error(err)
                    st.info(
                        "💡 **Why did this happen?**\n"
                        "This PDF contains image-only scans or vector paths with no digital/selectable text (words cannot be highlighted with a cursor).\n\n"
                        "**Quick solutions:**\n"
                        "1. **Use Searchable PDF**: Upload a searchable text version (a converted copy has been placed in your `Downloads` folder as `DataVisulizationLabSyllabus_searchable.pdf`).\n"
                        "2. **Enable AI OCR**: Add a `GEMINI_API_KEY` in `.env` or Streamlit secrets to let Gemini 2.0 Flash automatically OCR scanned documents."
                    )

    if clear_clicked:
        pipeline.reset()
        st.session_state["indexed_chunks"] = 0
        st.session_state["chat_history"] = []
        st.info("Knowledge base index and chat history have been cleared.")

    st.divider()
    st.metric(label="Total Chunks Indexed", value=st.session_state["indexed_chunks"])

    # Similarity Threshold Control
    sim_threshold = st.slider(
        "Similarity Threshold",
        min_value=0.05,
        max_value=0.50,
        value=0.20,
        step=0.01,
        help="Confidence cutoff: Lower values retrieve more broadly; higher values require tighter matches.",
    )
    pipeline.retriever.similarity_threshold = sim_threshold

    # Optional API key configuration
    st.divider()
    st.caption("Settings & Status")
    has_env_key = bool(GEMINI_API_KEY and GEMINI_MODEL)
    if has_env_key:
        st.caption(f"🤖 Gemini Key: Detected from .env (`{GEMINI_MODEL}`)")
    else:
        st.caption("📖 Gemini Key: Unset (Running in Offline Extractive Mode)")


# ==========================================
# MAIN INTERFACE: Question Answering
# ==========================================
st.title("Study Assistant: Document-Grounded Q&A")
st.markdown(
    "Ask any question grounded solely in your uploaded PDFs. "
    "Every answer includes exact file and page citations."
)

with st.form(key="qa_form", clear_on_submit=False):
    question_input = st.text_input(
        "Enter your question:",
        placeholder="e.g. What is the difference between supervised and unsupervised learning?",
    )
    submit_button = st.form_submit_button("Ask", type="primary")

if submit_button:
    clean_question = question_input.strip().strip('"\'“”`')
    if not clean_question:
        st.warning("Please enter a question before asking.")
    elif st.session_state["indexed_chunks"] == 0:
        st.error("No documents are currently indexed. Please upload and index PDF documents in the sidebar first.")
    else:
        with st.spinner("Searching relevant document sections and formulating answer..."):
            result = pipeline.ask(clean_question)

            st.session_state["chat_history"].insert(0, {
                "question": clean_question,
                "answer": result["answer"],
                "mode": result["mode"],
                "sources": result["sources"],
            })

# Render Q&A History
if st.session_state["chat_history"]:
    st.divider()
    st.subheader("Answers & Citations")

    for idx, item in enumerate(st.session_state["chat_history"]):
        with st.container():
            st.markdown(f"#### ❓ {item['question']}")
            st.markdown(item["answer"])

            # Mode Caption
            mode_display = {
                "gemini": "Gemini 2.0 (Synthesized)",
                "extractive": "Extractive Mode (Exact Quoted Passages)",
                "no_context": "No Matching Context Found",
            }.get(item["mode"], item["mode"].title())

            st.caption(f"Mode: **{mode_display}**")

            # Expandable Sources Section
            sources = item.get("sources", [])
            if sources:
                with st.expander(f"📄 Sources ({len(sources)} passage(s) retrieved)"):
                    for s_idx, src in enumerate(sources, start=1):
                        st.markdown(
                            f"**Passage {s_idx}** — Document: `{src['source']}` | Page: `{src['page']}` | "
                            f"Similarity Score: `{src['score']:.4f}`"
                        )
                        st.markdown(f"> {src['text']}")
                        if s_idx < len(sources):
                            st.divider()

            st.markdown("---")
