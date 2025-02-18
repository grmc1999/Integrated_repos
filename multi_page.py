import gradio as gr
import os
import sys
import tempfile
import zipfile

import integrated_utils as iu
from ChatBot_Newsletter.utils import base_utils as bu
from ChatBot_Newsletter.utils import retrieval_utils as ru

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


config = bu.load_config("ChatBot_Newsletter/configs/config.json")
embeddings_data = ru.load_embeddings(config["embeddings"]["output_dir"])
if not embeddings_data:
    print("No embeddings found. Please run generate_embeddings.py first.")
    sys.exit(1)
corpus_embeddings = embeddings_data["embeddings"]
segment_contents = embeddings_data["segment_contents"]
segment_sources = embeddings_data.get("segment_sources", [])
model_name = embeddings_data.get("model_name", "Unknown Model")
retrieval_model = ru.load_model(model_name)



demo = gr.Blocks(css="""
#resumos_textbox textarea {
  text-align: justify;
}
""")

with demo:
    with gr.Tab("Resumos Automáticos"):
        gr.Markdown(
            "## 🤖 Bem-vindo ao sistema de Resumos Automáticos!\n"
            "1. **Selecione** seus arquivos PDF, TXT ou DOCX.\n"
            "2. Clique em **Processar** para gerar os resumos.\n"
            "3. Acompanhe o progresso e veja os resumos aparecendo.\n"
            "4. Escolha o **Formato de saída** e clique em **Baixar** para baixar um .zip com os arquivos de resumo."
        )
        with gr.Column():
            files_input = gr.File(
                file_count="multiple", 
                label="Selecione seus arquivos para resumo"
            )
            process_button = gr.Button("Processar")
        output_box = gr.Textbox(
            label="Resumos Gerados",
            lines=15,
            elem_id="resumos_textbox"
        )
        summaries_state = gr.State()
        progress_slider = gr.Slider(
            minimum=0,
            maximum=100,
            value=0,
            step=1,
            label="Progresso (%)",
            interactive=False
        )
        process_button.click(
            fn=iu.process_files_with_progress,
            inputs=[files_input],
            outputs=[output_box, summaries_state, progress_slider],
            queue=True
        )
        with gr.Column():
            format_radio = gr.Radio(
                choices=["txt", "docx"], 
                label="Formato de saída", 
                value="txt"
            )
            download_button = gr.Button("Baixar")
        download_file = gr.File(label="Arquivo ZIP", interactive=False)

        download_button.click(
            fn=iu.create_zip_and_download,
            inputs=[summaries_state, format_radio],
            outputs=[download_file]
        )

    with gr.Tab("ChatBot"):
        chatbot = gr.ChatInterface(
            fn=iu.prep_response,
            type="messages",
            title="Chat Bot Basado no Boletim de Inteligência Competitiva",
            description="👋 Olá! Eu sou o assistente virtual baseado no Boletim de Inteligência Competitiva. Posso responder perguntas relacionadas às informações desse boletim."
        )

demo.launch(server_name="0.0.0.0", server_port=7860)