import json
import threading
import traceback
import pytchat
import time
from threading import Thread
from pluginInterface import InputPluginInterface
import gradio as gr
from liveTextbox import LiveTextbox
import requests
class Chess(InputPluginInterface):
    
    console_textbox = LiveTextbox()
    game_state_textbox = LiveTextbox()
    
    CHESS_SERVER_URL = 'http://localhost:8000/'
    
    engine_log = ""
    game_state = None
    processed_index = 0
    
    greeted = False
    played = False
    GREETING_PROMPT_TEMPLATE = "Your opponent has entered the game, greet your opponent. You are playing [side]. [first] goes first."
    
    def init(self):
        pass
    
    def create_ui(self):
        with gr.Accordion(label="Chess", open=False):
            with gr.Row():
                self.start_button = gr.Button("Start")
                self.get_engine_log_button = gr.Button("get engine log")
                self.make_move_button = gr.Button("make move")
                
            self.console_textbox.create_ui()
            self.game_state_textbox.create_ui()

        self.start_button.click(self.start_game)
        self.get_engine_log_button.click(self.get_engine_log)
        self.make_move_button.click(self.make_move)

    def get_engine_log(self): 
        try:
            response = requests.get(f"{self.CHESS_SERVER_URL}/engine_log")
            if response.status_code == 200:
                print("Successfully called the endpoint.")
                self.engine_log = response.text
                print(self.engine_log)  # Print the engine log or process it as needed
                self.process_engine_log()
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")
            
    def make_move(self): 
        try:
            response = requests.post(f"{self.CHESS_SERVER_URL}/make_move")
            if response.status_code == 200:
                print("Successfully called the endpoint.")
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")
    
    def start_game(self): 
        try:
            response = requests.post(f"{self.CHESS_SERVER_URL}/start_game")
            if response.status_code == 200:
                self.console_textbox.print("Game Started")
                try:
                    self.fetch_update_periodic()
                except KeyboardInterrupt:
                    print("Stopping...")
                    if self.update_loop: self.update_loop.cancel()
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")

        
            
    def fetch_update_periodic(self):
        try:
            response = requests.get(f"{self.CHESS_SERVER_URL}/game_state")
            if response.status_code == 200:
                self.game_state = response.json()
                self.game_state_textbox.set([json.dumps(self.game_state, indent=4)])
                self.process_update()
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")
        self.update_loop = threading.Timer(2, self.fetch_update_periodic).start()
        

    def process_update(self):
        # greeting
        if (self.game_state['joined'] == True) and not self.greeted:
            self.console_textbox.print(f"Opponent has joined.")
            self.greeted = True
            self.process_input(self.GREETING_PROMPT_TEMPLATE #.replace("[name]", self.game_state['opponent_name'])
                               .replace("[side]", self.game_state['side'])
                               .replace("[first]", "You" if self.game_state['side'] == "white" else "Opponent"))
        
        if (self.game_state['current_side'] == self.game_state['side']) and not self.played:
            self.console_textbox.print(f"Playing move.")
            self.played = True
            self.make_move()
    
            
    def process_engine_log(self):
        new_log = self.engine_log[self.processed_index:]
        # Extract initial position and moves
        position_line = [line for line in new_log.split("\n") if line.startswith(">> position")][0]
        moves_played = position_line.split("moves")[1].strip() if "moves" in position_line else "No moves have been played."

        # Parsing the final detailed engine output for depth 5
        final_line = [line for line in new_log.split("\n") if "info depth 5" in line][0]
        parts = final_line.split(" ")
        final_pv = " ".join(parts[parts.index("pv")+1:])
        best_move = parts[parts.index("pv")+1]
        final_score_cp = parts[parts.index("score")+2]
        final_wdl = parts[parts.index("wdl")+1:parts.index("wdl")+4]

        # Interpretation of the score
        score_description = "a balanced position" if int(final_score_cp) == 0 else ("an advantage for white" if int(final_score_cp) > 0 else "an advantage for black")

        # Format the prompt
        # prompt = f"""Given the following position in a chess game {moves_played}, the chess engine recommends the move sequence {final_pv}. The evaluation score is {final_score_cp}, indicating {score_description}. Can you explain the strategic motive behind these recommended moves and any significant implications they have on the game's outcome?"""
        prompt = f"""Given the following position in a chess game {moves_played}, Aya make the move {best_move}. Aya's analysis shows the evaluation score is {final_score_cp}, indicating {score_description}. State where Aya is moving what piece, and give a brief comment on the state of the game"""
        print(prompt)
        self.processed_index = len(self.engine_log)
        self.process_input(prompt)

