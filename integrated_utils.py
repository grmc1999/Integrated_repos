import os
import sys
import tempfile
import zipfile

from Authomatized_Summaries import utils as au
from ChatBot_Newsletter.utils import base_utils as bu
from ChatBot_Newsletter.utils import generation_utils as gu
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

def prep_response(message, history):
    """
    Function to generate the chatbot response based on the Competitive Intelligence Newsletter.
    """
    top_k = config["retrieve"]["top_k"]
    top_segments, top_similarities, top_sources = ru.search_query(
        message,
        corpus_embeddings,
        retrieval_model,
        segment_contents,
        segment_sources,
        top_k=top_k
    )

    context = "\n".join(top_segments)
    answer = gu.generate_answer(message, context, config)
    unique_references = set(top_sources)
    references_text = "\n".join(unique_references)

    response_text = (
        f"**Resposta do chatbot:**\n{answer}\n\n"
        f"**Referências:**\n{references_text}"
    )
    return response_text

def process_files_with_progress(files):
    """
    Converts the processing function into a generator (yield) to:
        1) Show real-time progress.
        2) Display partial summaries without waiting for all files to finish.
    
    This function will "yield" a tuple:
        (accumulated_summaries_text, summaries_dictionary, progress)
    in each iteration.
    """
    if not files:
        yield "Nenhum arquivo foi selecionado.", {}, 0
        return

    prompt_instructions = au.load_prompt(
        os.path.join("Authomatized_Summaries", "prompt.txt")
    )

    total_files = len(files)
    partial_text = ""
    partial_summaries = {}

    for idx, f in enumerate(files):
        base_name = os.path.basename(f.name)
        if base_name.lower().endswith(".pdf"):
            content = au.extract_text_from_pdf(f.name)
        elif base_name.lower().endswith(".txt"):
            with open(f.name, "r", encoding="utf-8") as infile:
                content = infile.read()
        elif base_name.lower().endswith(".docx"):
            content = "Extração de .docx não implementada neste exemplo."
        else:
            content = "Formato desconhecido ou não suportado."

        summary_data = au.generate_summary(client, content, prompt_instructions)
        partial_summaries[base_name] = summary_data

        partial_text += (
            f"{summary_data['title']}\n"
            f"{summary_data['content']}\n\n\n\n"
        )
        current_progress = int(((idx + 1) / total_files) * 100)
        yield partial_text, partial_summaries, current_progress


def download_summaries(summaries_dict, selected_format):
    """
    Creates a temporary ZIP file with the summaries in the selected format.
    """
    if not summaries_dict:
        return None

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "resumos.zip")

    with zipfile.ZipFile(zip_path, 'w') as zf:
        for filename, summary in summaries_dict.items():
            base = os.path.splitext(filename)[0] + "_summary"

            if selected_format == "txt":
                output_file = f"{base}.txt"
                full_out_path = os.path.join(tmp_dir, output_file)
                with open(full_out_path, 'w', encoding='utf-8') as f:
                    f.write(f"{summary['title']}\n\n{summary['content']}\n")
                zf.write(full_out_path, arcname=output_file)

            elif selected_format == "docx":
                output_file = f"{base}.docx"
                full_out_path = os.path.join(tmp_dir, output_file)
                au.save_summary(
                    output_folder=tmp_dir,
                    file_name=base,
                    summary=summary,
                    format="docx",
                )
                zf.write(full_out_path, arcname=output_file)

            else:
                pass
    return zip_path

def create_zip_and_download(summaries, chosen_format):
    """
    Creates a ZIP file with the summaries and downloads it.
    """
    zip_path = download_summaries(summaries, chosen_format)
    return zip_path
