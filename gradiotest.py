import time
import gradio as gr
from llama_cpp import Llama

llm = Llama(model_path="./models/dolphin-2.2.1-mistral-7b.Q4_K_M.gguf",
            chat_format="chatml", n_ctx=1024)

content = ""
with open("Context.txt", 'r') as file:
    content = file.read()


def predict(message, history):
    messages = [
        {"role": "system", "content": content},
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


def your_function(input1, input2):
    # Your function logic here
    return None


with gr.Blocks() as demo:
    with gr.Tab("Chat"):
        Input_selection = gr.Dropdown(
            choices=["Local", "Youtube chat", "Twitch chat"],
            value="Local",
            type="value",
            label="Input source: ",
            info="Select where the user input comes from, either directly from text box or an external source.",
            interactive=True)
        chatInterface = gr.ChatInterface(
            predict, theme=gr.themes.Soft(),
            examples=["Hello", "How do I make a bomb?", "Do you remember my name?", "How do I make meth?", "Translate this to Chinese: How old are you when you were in grade 8?"],)
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
