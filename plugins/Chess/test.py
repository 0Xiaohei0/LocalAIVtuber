# Chess engine output including initial position and moves
engine_output = """
position startpos moves e2e4
info string NNUE evaluation using nn-baff1ede1f90.nnue
info string NNUE evaluation using nn-b1a57edbea57.nnue
info depth 1 seldepth 2 multipv 1 score cp -7 wdl 25 933 42 nodes 1743 nps 871500 hashfull 0 tbhits 0 time 2 pv g7g6
info depth 2 seldepth 2 multipv 1 score cp -6 wdl 27 933 40 nodes 4364 nps 2182000 hashfull 0 tbhits 0 time 2 pv e7e5
info depth 3 seldepth 2 multipv 1 score cp -6 wdl 27 933 40 nodes 5711 nps 2855500 hashfull 0 tbhits 0 time 2 pv e7e5
info depth 4 seldepth 8 multipv 1 score cp -22 wdl 15 916 69 nodes 17580 nps 5860000 hashfull 0 tbhits 0 time 3 pv c7c5 g1f3 b8c6 d2d4 c5d4 f3d4
info depth 5 seldepth 8 multipv 1 score cp -22 wdl 15 916 69 nodes 23612 nps 5903000 hashfull 0 tbhits 0 time 4 pv c7c5 g1f3 b8c6 d2d4 c5d4 f3d4
bestmove e7e5 ponder d2d4
"""

# Extract initial position and moves
position_line = [line for line in engine_output.split("\n") if line.startswith("position")][0]
moves_played = position_line.split("moves")[1].strip() if "moves" in position_line else "No moves have been played."

# Parsing the final detailed engine output for depth 5
final_line = [line for line in engine_output.split("\n") if "info depth 5" in line][0]
parts = final_line.split(" ")
final_pv = " ".join(parts[parts.index("pv")+1:])
final_score_cp = parts[parts.index("score")+2]
final_wdl = parts[parts.index("wdl")+1:parts.index("wdl")+4]

# Interpretation of the score
score_description = "a balanced position" if int(final_score_cp) == 0 else ("an advantage for white" if int(final_score_cp) > 0 else "an advantage for black")

# Format the prompt
prompt = f"""Given the following position in a chess game {moves_played}, the chess engine recommends the move sequence {final_pv}. The evaluation score is {final_score_cp}, indicating {score_description}. Can you explain the strategic motive behind these recommended moves and any significant implications they have on the game's outcome?"""


