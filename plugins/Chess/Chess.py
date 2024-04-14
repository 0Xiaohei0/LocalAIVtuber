from enum import Enum, auto
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
from globals import GlobalKeys, global_state

class Chess(InputPluginInterface):
    
    console_textbox = LiveTextbox()
    game_state_textbox = LiveTextbox()
    
    CHESS_SERVER_URL = 'http://localhost:8000/'

    engine_log = ""
    game_state = None
    processed_index = 0
    
    request_sent = False
    GREETING_PROMPT_TEMPLATE = "Your opponent has entered the game."
    update_interval = 1
    move_interval = 2
    engine_log_interval = 30
    challenge_wait_interval = 15

    class States(Enum):
        IDLE = auto()
        GREET = auto()
        # THINK = auto()
        PLAY = auto()
        # WAIT = auto()

    def init(self):
        self.current_state = self.States.IDLE
    
    def create_ui(self):
        with gr.Accordion(label="Chess", open=False):
            with gr.Row():
                self.start_button = gr.Button("Start")
                self.start_opponent_button = gr.Button("Start Opponent")
                self.start_challenge_button = gr.Button("Start Challenge")
                #self.get_engine_log_button = gr.Button("get engine log")
                #self.make_move_button = gr.Button("make move")
                
            self.console_textbox.create_ui()
            self.game_state_textbox.create_ui()

        self.start_button.click(self.start_game)
        self.start_opponent_button.click(self.start_opponent)
        self.start_challenge_button.click(self.start_challenge)
        #self.get_engine_log_button.click(self.get_engine_log)
        #self.make_move_button.click(self.make_move)

    def get_engine_log(self): 
        try:
            response = requests.get(f"{self.CHESS_SERVER_URL}/engine_log")
            if response.status_code == 200:
                # print("Successfully called the endpoint.")
                self.engine_log = response.text
                self.process_engine_log()
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")
            
    def make_move(self): 
        try:
            response = requests.post(f"{self.CHESS_SERVER_URL}/make_move")
            if response.status_code == 200:
                # print("Successfully called the endpoint.")
                pass
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")
    
    def start_game(self): 
        try:
            response = requests.post(f"{self.CHESS_SERVER_URL}/start_game")
            if response.status_code == 200:
                self.console_textbox.print("Bot Started")
                try:
                    self.fetch_update_periodic()
                    self.get_engine_log_periodic()
                    self.continue_move_periodic()
                except KeyboardInterrupt:
                    print("Stopping...")
                    if self.update_loop: self.update_loop.cancel()
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")

    def start_opponent(self): 
        try:
            response = requests.post(f"{self.CHESS_SERVER_URL}/start_opponent")
            if response.status_code == 200:
                self.console_textbox.print("Opponent bot Started")
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")

    def start_challenge(self): 
        try:
            response = requests.post(f"{self.CHESS_SERVER_URL}/start_challenge")
            if response.status_code == 200:
                self.console_textbox.print("Challenge Started")
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")

    def continue_move_periodic(self):
        self.make_move()
        self.make_move_loop = threading.Timer(self.move_interval, self.continue_move_periodic).start()
            
    def fetch_update_periodic(self):
        try:
            response = requests.get(f"{self.CHESS_SERVER_URL}/game_state")
            if response.status_code == 200:
                self.game_state = response.json()
                self.game_state_textbox.set([json.dumps(self.game_state, indent=4), f"IS_IDLE: {global_state.get_value(GlobalKeys.IS_IDLE)}",
                                             f"State: {self.get_current_state()}"])
                self.process_update()
            else:
                print(f"Failed to call the endpoint. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error calling the endpoint: {e}")
        self.update_loop = threading.Timer(self.update_interval, self.fetch_update_periodic).start()
        
    def get_engine_log_periodic(self): 
        self.get_engine_log()
        self.engine_log_loop = threading.Timer(self.engine_log_interval, self.get_engine_log_periodic).start()
    def process_update(self):
        # print(f"self.current_state {self.current_state}")
        # print(f"self.game_state['joined'] {self.game_state['joined']}")
        # print(f"self.get_current_state == self.States.IDLE {self.get_current_state() == self.States.IDLE}")
        if self.get_current_state() == self.States.IDLE:
            self.processed_index = 0
            # greeting
            if (self.game_state['joined'] == True):
                self.console_textbox.print(f"Opponent has joined.")
                self.set_current_state(self.States.GREET)
                # self.process_input(self.GREETING_PROMPT_TEMPLATE #.replace("[name]", self.game_state['opponent_name'])
                #                 .replace("[side]", self.game_state['side'])
                #                 .replace("[first]", "You" if self.game_state['side'] == "white" else "Opponent"))
                
        elif self.get_current_state() == self.States.GREET:
            if (global_state.get_value(GlobalKeys.IS_IDLE) == True):
                self.set_current_state(self.States.PLAY)

        elif self.get_current_state() == self.States.PLAY:
            if (self.game_state['joined'] == False):
                self.processed_index = 0
                threading.Timer(self.challenge_wait_interval, self.start_challenge).start()
                self.set_current_state(self.States.IDLE)

        # elif self.get_current_state() == self.States.THINK:
        #     if (not self.request_sent):
        #         self.request_sent = True
        #         self.console_textbox.print(f"Getting chess module output")
        #         self.get_engine_log()
        #         self.console_textbox.print(f"Making move")
        #         self.make_move()
        #         self.set_current_state(self.States.PLAY)

        # elif self.get_current_state() == self.States.PLAY:
        #     if(self.is_idle()):
        #         self.set_current_state(self.States.WAIT)
        
        # elif self.get_current_state() == self.States.WAIT:
        #     if self.is_my_turn():
        #         self.set_current_state(self.States.THINK)

        # if (not self.get_current_state() == self.States.IDLE) and not self.game_state['joined']:
        #     self.set_current_state(self.States.IDLE)

    def is_idle(self) -> bool:
        return global_state.get_value(GlobalKeys.IS_IDLE) == True    
    
    def is_my_turn(self) -> bool:
        return self.game_state['current_side'] == self.game_state['side']
    
    def get_current_state(self) -> States:
        return self.current_state

    def set_current_state(self, state: States):
        self.current_state = state
        self.console_textbox.print(str(self.current_state))
    
            
    def process_engine_log(self):
        #new_log = self.engine_log[self.processed_index:]
        last_go_index = self.engine_log.rfind(">> go")
        new_log = self.engine_log[max(self.processed_index, last_go_index):]
        if not new_log:  # More pythonic way to check if the string is empty
            print("Waiting for new log.")
            self.get_engine_log()
            return  # Ensure that the function exits if no new log is available
        print(new_log)  # Print the engine log or process it as needed
        # Split once to avoid doing it multiple times
        log_lines = new_log.split("\n")

        # Using next() with a generator expression to safely access the first item or a default
        position_line = next((line for line in log_lines if line.startswith(">> position")), None)
        if position_line is None:
            moves_played = "Position line not found."
        else:
            moves_played = position_line.split("moves")[1].strip() if "moves" in position_line else "No moves have been played."

        # Similarly safeguarding access to the final line with "info depth 5"
        max_depth_line = next((line for line in reversed(log_lines) if "info depth" in line), None)
        if max_depth_line is None:
            print("Final detailed engine output not found.")
            return
    
        parts = max_depth_line.split(" ")

        try:
            final_pv_index = parts.index("pv")
            final_pv = " ".join(parts[final_pv_index+1:])
        except ValueError:
            final_pv = "N/A"

        try:
            final_score_cp = parts[parts.index("score")+2]
        except ValueError:
            final_score_cp = "N/A"

        try:
            final_wdl_index = parts.index("wdl")
            final_wdl = parts[final_wdl_index+1:final_wdl_index+4]
        except ValueError:
            final_wdl = "N/A"
            

        if final_score_cp != "N/A":
            # Interpretation of the score
            # score_description = "a balanced position" if int(final_score_cp) == 0 else ("an advantage for white" if int(final_score_cp) > 0 else "an advantage for black")
            score_description = "a balanced position" if int(final_score_cp) == 0 else ("an advantage for you" if int(final_score_cp) > 0 and self.game_state["side"] == "white" else "an advantage for your opponent")

        final_line = next((line for line in log_lines if "bestmove" in line), None)
        if final_line is None:
            print("Final detailed engine output not found.")
            # return
    
        #parts = final_line.split(" ")

        #best_move = parts[parts.index("bestmove") + 1] if "bestmove" in parts else "N/A"
        # Format the prompt
        # prompt = f"""Given the following position in a chess game {moves_played}, the chess engine recommends the move sequence {final_pv}. The evaluation score is {final_score_cp}, indicating {score_description}. Can you explain the strategic motive behind these recommended moves and any significant implications they have on the game's outcome?"""
        # prompt = f"""Given the following position in a chess game {moves_played}, I make the move {best_move}. Aya's analysis shows the evaluation score is {final_score_cp}, indicating {score_description}. State where Aya is moving what piece."""
        # prompt = f"""Given the following position in a chess game {moves_played}, The best move is {best_move}. Analysis shows the evaluation score is {final_score_cp}, indicating {score_description}. Given this data, state the move, and breifly talk about the situation In the perspective of Aya."""
        # prompt = f"""Given the following position in a chess game {moves_played}, The best move is {best_move}. Analysis shows the evaluation score is {final_score_cp}, indicating {score_description}. As Aya, playing {self.game_state['side']}, state your next move, assuming you have analyzed the position and found the best move on your own."""
        # prompt = f"""Given the best move is {best_move}. Describe your next move, assuming you have analyzed the position and found the best move on your own."""

        # prompt = f"""Analysis shows the evaluation score is {final_score_cp}, indicating {score_description}, your winrate for this game is {self.game_state['winrate']}%. You are playing {self.game_state['side']}. State your winrate. State if you or your opponent has the advantage."""
        prompt = f"""Here is the chess module output: Analysis shows the evaluation score is {final_score_cp}, indicating {score_description}. You are playing {self.game_state['side']}. State if you or your opponent has the advantage."""
        self.processed_index = len(self.engine_log)
        self.process_input(prompt)
        self.request_sent = False

