#libraries for image compositing
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageTk

import datetime

#cairo has some external dependencies
import os
folder_path = os.path.abspath("./cairo/bin/")
path_env_var = os.environ["PATH"]
if folder_path not in path_env_var:
    os.environ["PATH"] = folder_path + os.pathsep + path_env_var
    
#import these libraries for svg conversion
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

class template_image_full:
    def __init__(self, image_filename = ""):
        self.image_filename = image_filename

    fields = ['image_filename']

    def render(self):
        self.scalar_image = None
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

        if self.image_filename != "":
            #convert vector image type to scalar
            if self.image_filename.endswith(".svg"):
                try:
                    self.vector_image = svg2rlg(self.image_filename)
                    renderPM.drawToFile(self.vector_image, "scalar_image.png", fmt="PNG", dpi=100)
                    self.scalar_image = Image.open("scalar_image.png")
                except Exception as e:
                    print(f"unable to create badge from vector image: {e}")
            else:
                try:
                    self.scalar_image = Image.open(self.image_filename)
                    
                except:
                    print(f"no badge image file found: {e}")

            self.aspect_ratio = self.scalar_image.width / self.scalar_image.height

            #resize image to fill screen
            max_image_width = display_width - 2 * padding
            max_image_height = display_height - 2 * padding

            try:
                if self.scalar_image.height > max_image_height:
                    #portrait image. scale via height
                    self.scalar_image = self.scalar_image.resize((int(max_image_height * self.aspect_ratio), max_image_height))
                if self.scalar_image.width > max_image_width:
                    #landscape image. scale via width
                    self.scalar_image = self.scalar_image.resize((max_image_width, int(max_image_width / self.aspect_ratio)))
            except Exception as e:
                print(f"skipping badge: {e}")

            #self.scalar_image = self.scalar_image.resize((logo_height,int(logo_height/aspect_ratio)))
            self.im.paste(self.scalar_image,(int((display_width/2) - (self.scalar_image.width/2)), int((display_height/2) - (self.scalar_image.height/2) )))