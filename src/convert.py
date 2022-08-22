from typing import Tuple, Union

from values import *
import numpy as np
from PIL import Image
from tkinter import filedialog, Tk


def convert_img(width: int, height: int) -> Union[Tuple[np.ndarray, int, int], None]:
    Tk().withdraw()
    filename = filedialog.askopenfilename()
    if not filename:
        return
    img = Image.open(filename, mode="r")
    img.thumbnail((width//SCALE, height//SCALE))
    img.convert("RGB")

    offset_y, offset_x = img.size
    offset_y = ((height//SCALE)-offset_y)//2
    offset_x = ((width//SCALE)-offset_x)//2
    img = np.asarray(img, dtype=np.uint32)

    return img, offset_y, offset_x
