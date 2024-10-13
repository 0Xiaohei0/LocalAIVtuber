# Local AI Vtuber (A tool for hosting AI vtubers that runs fully locally and offline)

Full demo and setup guide: https://youtu.be/Yl-T3YgePmw?si=n-vaZzClw0Q833E5

- Chatbot, Translation and Text-to-Speech, all completely free and running locally.
- Support voice output in Japanese, English, German, Spanish, French, Russian and more, powered by RVC, silero and voicevox.
- Includes custom finetuned model to avoid generic chatbot responses and breaking character.
- Gradio UI web interface.
- plugin support for easily adding other providers.



<table>
  <tr>
    <td><img src="https://github.com/0Xiaohei0/VtuberChess/assets/24196833/6433bc1f-cdec-423f-b190-b7330497d28e" /></td>
    <td><img src="https://github.com/0Xiaohei0/VtuberChess/assets/24196833/5521eff5-4b36-4b13-9961-f4d7af8daded" /></td>
  </tr>
</table>


## Installation
### Manual setup (Tutorial video: [Full demo and setup guide](https://youtu.be/Yl-T3YgePmw?si=n-vaZzClw0Q833E5))
install python 3.10
https://www.python.org/downloads/release/python-3100/

install CUDA toolkit 12.4
https://developer.nvidia.com/cuda-12-4-0-download-archive

install visual studio and add desktop development with C++ component
https://visualstudio.microsoft.com/downloads/

![Screenshot 2024-10-03 100032](https://github.com/user-attachments/assets/11e56864-00ab-4c2d-931a-d9cc9422b52b)


#### 1. Download the project from [releases](https://github.com/0Xiaohei0/LocalAIVtuber/releases)
#### 2. open command prompt in project folder.
  
#### 3. Create environment
  ```
  python -m venv venv
  .\venv\Scripts\activate
  ```
  (If you encounter an error that says “cannot be loaded because the execution of scripts is disabled on this system. Open powershell with admin privilage and run ```Set-ExecutionPolicy RemoteSigned```)
  
#### 4. Install packages
  ```
  pip install -r requirements.txt
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
  pip install llama-cpp-python

  pip install nltk
  python -m nltk.downloader -d C:\nltk_data all
  ```

#### 5. Start Program
   ```
   python main.py
   ```
    When you see this message, go to http://localhost:7860 to see web UI 
    ```
    Running on local URL:  http://127.0.0.1:7860
    To create a public link, set `share=True` in `launch()`.
    ```

### Notes: 

#### restarting program

To start the program again, run:
  ```
  .\venv\Scripts\activate
   python main.py
   ```
#### run llm on gpu
If you have a decent GPU, You can install the GPU version of llama-cpp-python:
```
$env:CMAKE_ARGS ="-DGGML_CUDA=ON"
 pip install llama-cpp-python --force-reinstall --no-cache-dir --verbose --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/124
```
This can improve latency further.

Just a reminder for someone using Command Prompt instead of Power Shell
Change this
```
$env:CMAKE_ARGS ="-DGGML_CUDA=ON"
```
To this
```
set CMAKE_ARGS=-DGGML_CUDA=ON
```
or it will show error 
```
$env:CMAKE_ARGS ="-DGGML_CUDA=ON"
The filename, directory name, or volume label syntax is incorrect.
```

### One click setup (Outdated and may not work)
1. Download the project from [releases](https://github.com/0Xiaohei0/LocalAIVtuber/releases)
2. Extract and double click run.bat
3. When you see this message, go to http://localhost:7860 to see web UI 
```
Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.
```

## TODO (This project is still under development and more features are planned)
- Fetch chat input from streaming platforms (Finished)
- Improve local LLM (Finetuned model avaliable https://huggingface.co/xiaoheiqaq/Aya-7b-gguf)
- Write plugins for cloud providers(Azure tts, elevenlabs, chatgpt, whisper...)
- GPU support (Finished)
- Vtube studio integration (Finished)
- Let AI play games and provide commentary. (can currently play chess and keep talking nobody explode)
- AI singing



## FAQ:

- NameError: name '_in_projection' is not defined

You cannot enable gpt sovits and rvc at the same time, some of their modules have conflict. 

- UnboundLocalError: local variable 'response' referenced before assignment

  If you cloned this repo, you maybe missing model files for gpt-sovits, which will be in the zip folder in the [releases](https://github.com/0Xiaohei0/LocalAIVtuber/releases) section. 
  replace plugins\gpt_sovits\models with the one from the zip.
- To fetch chat from Youtube, copy the youtube_video_id from the stream url like this:
  
 ![image](https://github.com/0Xiaohei0/LocalAIVtuber/assets/24196833/942b9811-46bc-40f9-a7df-7938d0070513)

Then press start fetching chat

![image](https://github.com/0Xiaohei0/LocalAIVtuber/assets/24196833/96b8a971-00e8-4930-a9b4-897b3ddf27bf)


