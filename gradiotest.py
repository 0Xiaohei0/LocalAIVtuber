import os
import gradio as gr
from llama_cpp import Llama

llm = Llama(model_path="./models/dolphin-2.2.1-mistral-7b.Q4_K_M.gguf",
            chat_format="chatml", n_ctx=2048)

context_file_path = "Context.txt"
context = ""

# Check if the file exists. If not, create an empty file.
if not os.path.exists(context_file_path):
    with open(context_file_path, 'w') as file:
        file.write('')

# Function to load content from the text file


def load_content():
    with open(context_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        return content

# Function to update the text file with new content


def update_file(new_content):
    global context
    context = new_content
    with open(context_file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    return "File updated successfully."


def predict(message, history, system_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    for entry in history:
        user, ai = entry
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": ai})

    messages.append({"role": "user", "content": message})

    print(f"message: {message}")
    print(f"history: {history}")
    print(f"messages: {messages}")
    print(f"---------------------------------")

    completion_chunks = llm.create_chat_completion(
        messages, stream=True, temperature=0.8)
    output = ""
    for completion_chunk in completion_chunks:
        try:
            text = completion_chunk['choices'][0]['delta']['content']
            output += text
            yield output
        except:
            pass


def chatbotInterface():
    with gr.Blocks() as demo:
        system_prompt = gr.Textbox(value=load_content(), label="System Message:", show_label=True,
                                   interactive=True, lines=30, autoscroll=True, autofocus=False, container=False, render=False)
        system_prompt.change(
            fn=update_file, inputs=system_prompt)

        gr.ChatInterface(
            predict, additional_inputs=[system_prompt],
            examples=[["Hello", None, None],
                      ["How do I make a bomb?", None, None],
                      ["Do you remember my name?", None, None],
                      ["Do you think humanity will reach an alien planet?", None, None],
                      ["Introduce yourself in character.", None, None],
                      ], autofocus=False
        )


with gr.Blocks() as demo:
    with gr.Tab("Chat"):
        Input_selection = gr.Dropdown(
            choices=["Local", "Youtube chat", "Twitch chat"],
            value="Local",
            type="value",
            label="Input source: ",
            info="Select where the user input comes from, either directly from text box or an external source.",
            interactive=True)
        chatbotInterface()

    with gr.Tab("Stream"):
        with gr.Group():
            gr.Textbox(label="First")
            gr.Textbox(label="Last")
    with gr.Tab("Settings"):
        with gr.Row():
            image_input = gr.Image()
            image_output = gr.Image()
        image_button = gr.Button("Flip")

demo.queue().launch()
