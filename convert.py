from typing import Tuple

from values import *
from numpy import array
from PIL import Image
from tkinter import filedialog, Tk


def convert_img() -> Tuple[array, int, int]:
    Tk().withdraw()
    filename = filedialog.askopenfilename()
    if not filename:
        return
    img = Image.open(filename, mode="r")
    img.thumbnail([WX//SCALE, WY//SCALE])
    img.convert("RGB")

    offset_y, offset_x = img.size
    offset_y = ((WY//SCALE)-offset_y)//2
    offset_x = ((WX//SCALE)-offset_x)//2
    img = array(img)

    return img, offset_y, offset_x
