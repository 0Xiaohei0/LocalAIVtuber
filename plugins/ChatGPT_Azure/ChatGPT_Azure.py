import sys
import requests
from pluginInterface import LLMPluginInterface
import gradio as gr
from openai import AzureOpenAI
import os
from configManager import config_manager

class ChatGPT_Azure(LLMPluginInterface):
    context_length = 4096
    temperature = 0.9

    plugin_config = config_manager.load_section("ChatGPT_Azure")
    api_key = plugin_config.get("api_key")
    api_version = plugin_config.get("api_version")
    azure_endpoint = plugin_config.get("azure_endpoint")
    model_name = plugin_config.get("model_name")

    def init(self):
        self.client = None

    def create_ui(self):
        with gr.Accordion("ChatGPT_Azure settings", open=False):
            with gr.Row():
                self.api_key_Input = gr.Textbox(label="API key", value=self.api_key)
                self.api_key_Input.change(fn=self.update_api_key,inputs=self.api_key_Input)

                self.api_version_Input = gr.Textbox(label="API version", value=self.api_version)
                self.api_version_Input.change(fn=self.update_api_version,inputs=self.api_version_Input)

                self.azure_endpoint_Input = gr.Textbox(label="azure_endpoint", value=self.azure_endpoint)
                self.azure_endpoint_Input.change(fn=self.update_azure_endpoint,inputs=self.azure_endpoint_Input)

                self.model_name_Input = gr.Textbox(label="model_name", value=self.model_name)
                self.model_name_Input.change(fn=self.update_model_name,inputs=self.model_name_Input)

    def update_api_key(self, value):
        self.api_key = value
        config_manager.save_config("ChatGPT_Azure", "api_key", value)

    def update_api_version(self, value):
        self.api_version = value
        config_manager.save_config("ChatGPT_Azure", "api_version", value)
    
    def update_azure_endpoint(self, value):
        self.azure_endpoint = value
        config_manager.save_config("ChatGPT_Azure", "azure_endpoint", value)

    def update_model_name(self, value):
        self.model_name = value
        config_manager.save_config("ChatGPT_Azure", "model_name", value)

    def predict(self, message, history, system_prompt):
        if self.client is None:
            self.client = AzureOpenAI(
                api_key=self.api_key,  
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint
            )
        
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        for entry in history:
            user, ai = entry
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": ai})
        
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,  
            top_p=1.0,
            stream=True
        )

        output = ""
        for chunk in response:
            try:
                print(chunk.choices[0].delta.content  or "", end="")
                output += chunk.choices[0].delta.content
                yield output
            except Exception as e:
                print(f"Error: {e}")