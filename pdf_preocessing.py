import gradio as gr
from gradio_pdf import PDF
#from pdf2image import convert_from_path
#from transformers import pipeline
from pathlib import Path

iface = gr.Interface(fn=lambda files:[file.obj_name for file in files],
                     inputs=gr.components.File(file_count="multiple", label=None),
                     outputs="text")

iface.launch()