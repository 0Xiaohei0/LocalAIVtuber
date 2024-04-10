# Chess engine output including initial position and moves
engine_output = """
>> ucinewgame
>> isready
<< readyok
>> position startpos
>> go depth 5 movetime 10
<< info string NNUE evaluation using nn-baff1ede1f90.nnue
<< info string NNUE evaluation using nn-b1a57edbea57.nnue
<< info depth 1 seldepth 2 multipv 1 score cp 0 wdl 33 935 32 nodes 880 nps 440000 hashfull 0 tbhits 0 time 2 pv d2d4
<< info depth 2 seldepth 2 multipv 1 score cp 52 wdl 173 822 5 nodes 2184 nps 1092000 hashfull 0 tbhits 0 time 2 pv d2d4
<< info depth 3 seldepth 3 multipv 1 score cp 40 wdl 119 873 8 nodes 5278 nps 2639000 hashfull 0 tbhits 0 time 2 pv c2c4
<< info depth 4 seldepth 5 multipv 1 score cp 28 wdl 84 904 12 nodes 9478 nps 3159333 hashfull 0 tbhits 0 time 3 pv d2d4 d7d5 b1d2 e7e6
<< info depth 5 seldepth 6 multipv 1 score cp 26 wdl 77 909 14 nodes 16471 nps 5490333 hashfull 0 tbhits 0 time 3 pv e2e4 d7d5 e4d5 d8d5 d2d4
<< bestmove g1f3 ponder d7d5

"""

def process_engine_log():
        global engine_output
        log_lines = engine_output.split("\n")

        # Using next() with a generator expression to safely access the first item or a default
        position_line = next((line for line in log_lines if line.startswith(">> position")), None)
        if position_line is None:
            moves_played = "Position line not found."
        else:
            moves_played = position_line.split("moves")[1].strip() if "moves" in position_line else "No moves have been played."

        # Similarly safeguarding access to the final line with "info depth 5"
        max_depth_line = next((line for line in log_lines if "info depth 5" in line), None)
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
            score_description = "a balanced position" if int(final_score_cp) == 0 else ("an advantage for white" if int(final_score_cp) > 0 else "an advantage for black")


        final_line = next((line for line in log_lines if "bestmove" in line), None)
        if final_line is None:
            print("Final detailed engine output not found.")
            return
    
        parts = final_line.split(" ")

        best_move = parts[parts.index("bestmove") + 1] if "bestmove" in parts else "N/A"

        # Format the prompt
        # prompt = f"""Given the following position in a chess game {moves_played}, the chess engine recommends the move sequence {final_pv}. The evaluation score is {final_score_cp}, indicating {score_description}. Can you explain the strategic motive behind these recommended moves and any significant implications they have on the game's outcome?"""
        # prompt = f"""Given the following position in a chess game {moves_played}, I make the move {best_move}. Aya's analysis shows the evaluation score is {final_score_cp}, indicating {score_description}. State where Aya is moving what piece."""
        prompt = f"""Given the following position in a chess game {moves_played}, Aya make the move {best_move}. State where Aya is moving what piece."""
        
        print(prompt)

process_engine_log()