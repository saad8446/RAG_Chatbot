import gradio as gr
import os
import PyPDF2
import docx
import tempfile
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


client = Groq(api_key=GROQ_API_KEY)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


vector_db = {
    "chunks": [],
    "embeddings": [],
    "metadata": []
}

# LOGIC (BACKEND) ---

def extract_text_from_file(file_path):
    filename = os.path.basename(file_path)
    text_data = []
    
    if filename.endswith('.pdf'):
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        text_data.append({"text": text, "source": f"{filename} (Page {i+1})"})
        except Exception as e:
            print(f"Error reading PDF {filename}: {e}")

    elif filename.endswith('.docx'):
        try:
            doc = docx.Document(file_path)
            for i, para in enumerate(doc.paragraphs):
                if para.text.strip():
                    text_data.append({"text": para.text, "source": f"{filename} (Para {i+1})"})
        except Exception as e:
            print(f"Error reading DOCX {filename}: {e}")
            
    return text_data

def process_files(files, progress=gr.Progress()):
    global vector_db
    
    if not files:
        return "⚠️ Upload files first.", gr.update(interactive=False)

    progress(0.1, desc="Scanning Documents...")
    all_documents = []
    
    for file_path in files:
        file_docs = extract_text_from_file(file_path)
        all_documents.extend(file_docs)

    if not all_documents:
        return "❌ No readable text found.", gr.update(interactive=False)

    progress(0.4, desc="Indexing Knowledge...")
    chunks = []
    sources = []
    chunk_size = 1000
    overlap = 200
    
    for doc in all_documents:
        text = doc["text"]
        source = doc["source"]
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            sources.append(source)
            start += (chunk_size - overlap)

    progress(0.7, desc="Vectorizing Data...")
    embeddings = embedding_model.encode(chunks)
    
    vector_db["chunks"] = chunks
    vector_db["embeddings"] = embeddings
    vector_db["metadata"] = sources
    
    return f"✅ NEXUS ONLINE. Indexed {len(chunks)} data points.", gr.update(interactive=True)

def chat_logic(message, history, response_level):
    if not vector_db["chunks"]:
        return history + [[message, "⚠️ System Offline. Please upload documents to initialize."]]
        
    query_embedding = embedding_model.encode([message])
    similarities = cosine_similarity(query_embedding, vector_db["embeddings"])[0]
    top_indices = similarities.argsort()[-3:][::-1] 
    
    retrieved_context = []
    used_sources = []
    
    for idx in top_indices:
        chunk = vector_db["chunks"][idx]
        source = vector_db["metadata"][idx]
        retrieved_context.append(chunk)
        used_sources.append(source)

    context_str = "\n\n".join(retrieved_context)
    
    unique_sources = list(set(used_sources))
    footer = "\n\n🔍 **References:**\n" + "\n".join([f"• {s}" for s in unique_sources])
    
    if response_level == 1:
        instruction = "Be concise. Bullet points preferred."
    elif response_level == 2:
        instruction = "Be helpful and professional. Explain clearly."
    else: 
        instruction = "Be extremely detailed and comprehensive."

    system_prompt = f"""You are NEXUS AI. Answer using ONLY the Context below.
    If the answer is not found, say "Data not found in archives."
    
    Instruction: {instruction}
    
    --- CONTEXT START ---
    {context_str}
    --- CONTEXT END ---
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.5
        )
        response = completion.choices[0].message.content + footer
    except Exception as e:
        response = f"System Error: {str(e)}"

    history.append((message, response))
    return history

def download_history(history):
    if not history:
        return None
    content = "--- NEXUS AI SESSION LOG ---\n\n"
    for turn in history:
        content += f"USER: {turn[0]}\nNEXUS: {turn[1]}\n" + "-" * 40 + "\n"
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", encoding='utf-8') as f:
        f.write(content)
        return f.name

# --- 4. VISUALS (CSS) ---
custom_css = """
body { background-color: #0b0f19; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
.gradio-container { background-color: #0b0f19 !important; border: none; }
.contain { background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; }

.gradient-text {
    background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3em;
    font-weight: 900;
    text-align: center;
    letter-spacing: 2px;
}
.sub-text {
    text-align: center;
    color: #94a3b8;
    font-size: 1.1em;
    margin-bottom: 25px;
}
button.primary { 
    background: linear-gradient(135deg, #6366f1, #9333ea); 
    color: white; 
    font-weight: bold; 
    border: none; 
    transition: 0.3s;
}
button.primary:hover { box-shadow: 0 0 15px rgba(139, 92, 246, 0.5); }
#chatbot { height: 600px !important; background-color: #111827; border: 1px solid #374151; }
"""

# --- 5. UI LAYOUT ---
with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as app:
    
    gr.HTML("""
    <div class="gradient-text">NEXUS AI</div>
    <div class="sub-text">Neural Knowledge Engine • Multi-Format Support</div>
    """)
    
    with gr.Row():
        
        # LEFT COLUMN
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### 📡 DATA INGESTION")
            file_input = gr.File(
                file_count="multiple", 
                file_types=[".pdf", ".docx"],
                label="Upload Documents"
            )
            process_btn = gr.Button("⚡ ACTIVATE SYSTEM", variant="primary")
            status_txt = gr.Textbox(label="System Status", interactive=False, value="Standby", max_lines=1)
            
            gr.Markdown("---")
            gr.Markdown("### 🎛️ CONFIGURATION")
            level_slider = gr.Slider(
                minimum=1, maximum=3, step=1, value=2, 
                label="Response Detail Level"
            )
            
            gr.Markdown("### 💾 SESSION DATA")
            download_btn = gr.Button("📥 Export Chat Log")
            download_file = gr.File(label="Download Link", interactive=False, visible=True)

        # RIGHT COLUMN
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="NEXUS INTERFACE", elem_id="chatbot", layout="bubble")
            
            # --- INPUT BAR ROW ---
            with gr.Row():
                msg_input = gr.Textbox(
                    scale=4, 
                    show_label=False, 
                    placeholder="Enter your query here...",
                    container=False
                )
                send_btn = gr.Button("Send", scale=1, variant="primary")
                clear_btn = gr.Button("🗑️", scale=0, variant="stop", min_width=50)

    # --- EVENT HANDLERS ---
    process_btn.click(
        fn=process_files,
        inputs=file_input,
        outputs=[status_txt, msg_input]
    )

    send_btn.click(
        fn=chat_logic,
        inputs=[msg_input, chatbot, level_slider],
        outputs=[chatbot]
    ).then(fn=lambda: "", outputs=[msg_input])
    
    msg_input.submit(
        fn=chat_logic,
        inputs=[msg_input, chatbot, level_slider],
        outputs=[chatbot]
    ).then(fn=lambda: "", outputs=[msg_input])

    download_btn.click(fn=download_history, inputs=[chatbot], outputs=[download_file])
    
    # Clear Button Logic
    clear_btn.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    app.launch()