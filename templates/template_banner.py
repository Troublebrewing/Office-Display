#libraries for image compositing
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageTk

import datetime

class template_banner:
    def __init__(self, text="Banner Text", color="black"):
        self.text = text  
        self.color = color      

    fields = ['text', 'color']

    def render(self):
        display_width = 800
        display_height = 480

        self.im = Image.new(mode="RGB", size=(display_width,display_height), color="white")

        self.im2 = ImageDraw.Draw(self.im)
        self.im2.fontmode = "1"  #turns off text anti aliasing. quantization gets weird if this is on

        #colors      #0xBBGGRR
        EPD_BLACK   = 0x000000
        EPD_WHITE   = 0xFFFFFF
        EPD_GREEN   = 0x00FF00
        EPD_BLUE    = 0xFF0000
        EPD_RED     = 0x0000FF
        EPD_YELLOW  = 0x00FFFF
        EPD_ORANGE  = 0x007DFF

        padding = 10
        
        max_width = display_width - 2 * (padding)
        
        statusfont2_size = 120

        while True:
            statusfont2 = ImageFont.truetype('fonts/Inter_28pt-Bold.ttf', statusfont2_size)
            boundingbox = self.im2.textbbox((0, 0), self.text.upper(), font=statusfont2)
            #anchor = (display_width/2)-((boundingbox[2]-boundingbox[0])/2)
            text_width = boundingbox[2] - boundingbox[0]
            text_height = boundingbox[3] - boundingbox[1]
            if text_width <= max_width:
                break
            statusfont2_size -= 1

        anchor_x = (display_width - text_width) / 2
        anchor_y = ((display_height / 2) - text_height) + padding
        self.im2.text((anchor_x, anchor_y), self.text.upper(), font=statusfont2, fill=self.color)


        