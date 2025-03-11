from llama_cpp import Llama

from llama_cpp.llama_chat_format import MoondreamChatHandler
import base64
import pyautogui

def image_to_base64_data_uri(file_path):
    with open(file_path, "rb") as img_file:
        base64_data = base64.b64encode(img_file.read()).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"

class VisionLLM:
    def __init__(self):
        self.chat_handler = MoondreamChatHandler.from_pretrained(
            repo_id="vikhyatk/moondream2",
            filename="*mmproj*",
        )

        self.llm = Llama.from_pretrained(
            repo_id="vikhyatk/moondream2",
            filename="*text-model*",
            chat_handler=self.chat_handler,
            n_ctx=2048, # n_ctx should be increased to accommodate the image embedding
            n_gpu_layers=0
        )

    def get_image_description(self, image_url):
        data_uri = image_to_base64_data_uri(image_url)
        response = self.llm.create_chat_completion(
            messages = [
                {"role": "system", "content": "You are an assistant who perfectly describes images."},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_uri }},
                        {"type" : "text", "text": "Describe this image in detail please. state any text in the image if present."}
                    ]
                }
            ]
        )
        return response["choices"][0]["message"]["content"]
    
    def get_screen_description(self):
        screenshot = pyautogui.screenshot()
        screenshot.save("screen.png")
        return self.get_image_description("screen.png")