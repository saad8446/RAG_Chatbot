# 📄 Project Report: NEXUS AI Chatbot

**Student Name:** M Saad 
**Hugging Face Space:** [https://huggingface.co/spaces/saad8446/Nexus_AI_chatbot](https://huggingface.co/spaces/saad8446/Nexus_AI_chatbot)  
**GitHub Repository:** [https://github.com/saad8446/RAG_Chatbot](https://github.com/saad8446/RAG_Chatbot)

## 1. Project Overview
NEXUS AI is an advanced **Retrieval-Augmented Generation (RAG)** chatbot designed to bridge the gap between static documents and dynamic conversation. Built using **Python, Gradio, and Groq (Llama 3)**, the system allows users to upload technical documentation (PDFs and DOCX files) and query them in natural language. The system retrieves relevant semantic chunks using vector embeddings and generates accurate, context-aware responses, eliminating the need to manually search through hundreds of pages.

## 2. Key Features & Enhancements
Beyond the base requirements, I implemented **5 advanced enhancements** to improve user experience and system robustness:

1.  **Multi-Format Support:** Added `python-docx` integration to support Word Documents (.docx) alongside standard PDFs.
2.  **Smart Source Citations:** The bot provides transparency by listing exact filenames and page/paragraph numbers for every answer.
3.  **Conversational Memory:** Implemented state management so users can ask follow-up questions without losing context.
4.  **Chat History Export:** Added a "Download Log" feature that serializes the session into a `.txt` file for documentation.
5.  **Sentence Transformers:** replaced basic TF-IDF with `all-MiniLM-L6-v2` for state-of-the-art semantic vector search.

## 3. Screenshots
*(Paste 2-3 screenshots here. Recommended: 1 showing the "Cyberpunk" UI with the gradient header, and 1 showing a chat response with source citations)*

## 4. Challenges Faced & Solutions
* **Challenge:** Handling different file structures (PDF pages vs. Word paragraphs) required different extraction logic.
    * *Solution:* I wrote a modular `extract_text_from_file` function that detects the file extension and switches parsing libraries automatically.
* **Challenge:** Ensuring the LLM sticks strictly to the provided context.
    * *Solution:* I used strict system prompting ("Answer using ONLY the Context below") and engineered a fallback message ("Data not found") to prevent hallucinations.
* **Challenge:** Creating a unique visual identity in Gradio.
    * *Solution:* I learned to inject custom CSS to override Gradio's default theme, creating the "Neon/Dark Mode" aesthetic.# RAG_Chatbot
