import gradio as gr
import random
import time
from Authomatized_Summaries import utils
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)


def files_processing(files,output_format):

    news = utils.load_news_from_list(files)

    for file_name, content in news:

        summary = utils.generate_summary(client, content, prompt_instructions)
        output_file_name = file_name.rsplit(".", 1)[0] + "_summary"
        utils.save_summary(output_folder, output_file_name, summary, format=output_format)

        print(f"Summary saved to: ../output/{output_file_name}.{output_format}")


    return output_type

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
                     gr.Radio([".pdf", ".docx"]),
                     #gr.FileExplorer()
                     ],
                     outputs="text")

with demo.route("Automatic Summaries") as incrementer_demo:
    iface.render()


#with demo.route("Chatbot") as incrementer_demo:

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
