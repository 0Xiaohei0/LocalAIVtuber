import tkinter as tk
from PIL import Image, ImageTk
import chess
import chess.svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image
from io import BytesIO


class ChessApp:
    def __init__(self, root):
        self.root = root
        self.board = chess.Board()
        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack()
        self.draw_board()

    def svg_to_photoimage(self, svg_string):
       # Convert SVG string to a ReportLab Graphics Object
        drawing = svg2rlg(BytesIO(svg_string.encode('utf-8')))

        # Render to a PIL Image
        png_image = renderPM.drawToPIL(drawing)

        # Use Pillow to open this file-like object as an image
        image = Image.open(png_image)
        photo = ImageTk.PhotoImage(image)
        return photo

    def draw_board(self):
        # Generate SVG string from the current board state
        svg_string = chess.svg.board(self.board)
        image = self.svg_to_photoimage(svg_string)
        self.canvas.create_image(200, 200, image=image)


root = tk.Tk()
app = ChessApp(root)
root.mainloop()
