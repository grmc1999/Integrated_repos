import gradio as gr
import random
import time
import sys
from Authomatized_Summaries import utils
from ChatBot_Newsletter.utils import base_utils as bu
from ChatBot_Newsletter.utils.generation_utils import generate_answer
from ChatBot_Newsletter.utils.retrieval_utils import load_embeddings, load_model, search_query
from openai import OpenAI
import openai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
#openai.api_key = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=api_key)


# Chatbot setting

config = bu.load_config("ChatBot_Newsletter/configs/config.json")

embeddings_data = load_embeddings(config["embeddings"]["output_dir"])
if not embeddings_data:
    print("No embeddings found. Please run generate_embeddings.py first.")
    sys.exit(1)
corpus_embeddings = embeddings_data["embeddings"]
segment_contents = embeddings_data["segment_contents"]
segment_sources = embeddings_data.get("segment_sources", [])
model_name = embeddings_data.get("model_name", "Unknown Model")
retrieval_model = load_model(model_name)

def prep_response(message, history):
    top_k = config["retrieve"]["top_k"]
    top_segments, top_similarities, top_sources = search_query(
            message,
            corpus_embeddings,
            retrieval_model,
            segment_contents,
            segment_sources,
            top_k=top_k
        )

    print("\nSegmentos recuperados:\n-------------------")
    response="\nSegmentos recuperados:\n-------------------"
    for i, (segment, source) in enumerate(zip(top_segments, top_sources)):
        score = float(top_similarities[i])
        print(f"Segmento {i+1} (similaridade={score:.4f}) da fonte '{source}':\n{segment}\n")
        response=response+f"Segmento {i+1} (similaridade={score:.4f}) da fonte '{source}':\n{segment}\n"
    context = "\n".join(top_segments)
    answer = generate_answer(message, context, config)
    unique_references = set(top_sources)
    references_text = "\n".join(unique_references)
    print("Resposta do chatbot:\n--------------------")
    response=response+"Resposta do chatbot:\n--------------------"
    print(answer)
    response=response+answer
    print("\nReferências:\n--------------------")
    response=response+references_text+"\nReferências:\n--------------------"
    print(references_text)
    response=response+references_text
    return response


def files_processing(files,output_format):

    news = utils.load_news_from_list(files)

    prompt_instructions = utils.load_prompt(
        os.path.join("Authomatized_Summaries","prompt.txt")
        )

    Summaries={}

    for file_name, content in news:

        summary = utils.generate_summary(client, content, prompt_instructions)
        print(file_name.split("/")[-1])
        output_file_name = file_name.split("/")[-1].rsplit(".", 1)[0] + "_summary"
        print(os.path.join("output","{output_file_name}.{output_format}"))
        utils.save_summary(
            os.path.join("..","output"),
           # "../output/{output_file_name}.{output_format}",
        output_file_name, summary, format=output_format)

        print(f"Summary saved to: ../output/{output_file_name}.{output_format}")
        Summaries.update({
            file_name:summary
        })


    return Summaries

with gr.Blocks() as demo:
    name = gr.Textbox(label="Name")
    output = gr.Textbox(label="Output Box")
    greet_btn = gr.Button("Greet")
    @gr.on([greet_btn.click, name.submit], inputs=name, outputs=output)
    def greet(name):
        return "Hello " + name + "!"
    
    @gr.render(inputs=name, triggers=[output.change])
    def spell_out(name):
        with gr.Row():
            for letter in name:
                gr.Textbox(letter)


#operation = gr.Radio([".pdf", ".docx"])
iface = gr.Interface(fn=files_processing,
                     inputs=[gr.components.File(file_count="multiple", label=None),
                     gr.Radio(["txt", "docx"]),
                     #gr.FileExplorer()
                     ],
                     outputs="text")

with demo.route("Automatic Summaries") as incrementer_demo:
    iface.render()


with demo.route("Chatbot") as incrementer_demo:
    gr.ChatInterface(
        fn=prep_response, 
        type="messages"
    )

with demo.route("Up") as incrementer_demo:
    num = gr.Number()
    incrementer_demo.load(lambda: time.sleep(1) or random.randint(10, 40), None, num)

    with gr.Row():
        inc_btn = gr.Button("Increase")
        dec_btn = gr.Button("Decrease")
    inc_btn.click(fn=lambda x: x + 1, inputs=num, outputs=num, api_name="increment")
    dec_btn.click(fn=lambda x: x - 1, inputs=num, outputs=num, api_name="decrement")
    for i in range(100):
        gr.Textbox()

def wait(x):
    time.sleep(2)
    return x

identity_iface = gr.Interface(wait, "image", "image")

with demo.route("Interface") as incrementer_demo:
    identity_iface.render()
    gr.Interface(lambda x, y: x * y, ["number", "number"], "number")

demo.launch()
