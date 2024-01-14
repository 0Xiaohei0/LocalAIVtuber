from llama_cpp import Llama


def predict(message, history):
    llm = Llama(model_path="./models/mistral-7b-openorca.Q5_K_M.gguf",
                chat_format="chatml")

    output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a Japanese girl streaming chess, you are training your skill in a game with an AI opponent."},
            {
                "role": "user",
                "content": "The opponent has pinned your queen."
            }
        ]
    )
    print(output)
