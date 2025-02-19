import os
import time
import datetime
from dotenv import load_dotenv
from openai import OpenAI
import utils

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

input_folder = "input"
prompt_path = "prompt.txt"
output_format = "docx"  # "docx" or "txt"
output_folder = "output/docx" if output_format == "docx" else "output/txt"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

prompt_instructions = utils.load_prompt(prompt_path)

news = utils.load_news(input_folder)

start_time = time.time()

for file_name, content in news:

    summary = utils.generate_summary(client, content, prompt_instructions)
    output_file_name = file_name.rsplit(".", 1)[0] + "_summary"
    utils.save_summary(output_folder, output_file_name, summary, format=output_format)
    
    print(f"Summary saved to: {output_folder}/{output_file_name}.{output_format}")

end_time = time.time()
execution_time = end_time - start_time

formatted_time = str(datetime.timedelta(seconds=int(execution_time)))
print(f"Total execution time: {formatted_time}")