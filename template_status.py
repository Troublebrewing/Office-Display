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

class template_status:
    def __init__(self, name="Dixon Dan", title="Head Honcho", badge_filename="", status="Available", status_color="", banner_text=""):
        self.name = name
        self.title = title
        self.badge_filename = badge_filename
        self.status = status
        self.status_color = status_color
        self.banner_text = banner_text
    
    fields = ['name', 'title', 'badge_filename', 'status', 'status_color', 'banner_text']

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
        
        #if color is specified, use that
        if self.status_color != "":
            bordercolor = self.status_color
            statuscolor = self.status_color
        else:
            #color not specified
            # look for keywords in status              
            if self.status == "Focus":
                bordercolor = EPD_YELLOW
                statuscolor = EPD_YELLOW
            elif (self.status == "Busy") or (self.status == "Out of Office"):
                bordercolor = EPD_RED
                statuscolor = EPD_RED
            elif self.status == "Available":
                bordercolor = EPD_GREEN
                statuscolor = EPD_GREEN
            else:
                # no color specified and no keywords found
                # default colors
                bordercolor = EPD_WHITE
                statuscolor = EPD_BLACK 
        
        

        #outline
        borderwidth = 20
        padding = 10
        self.im2.rectangle([(0,0),(display_width-1,display_height-1)], fill=None, outline=bordercolor, width=borderwidth)

        # time
        timefont = ImageFont.truetype('fonts/Inter_28pt-Bold.ttf', 35)
        now = datetime.datetime.now()
        #print(now)
        #date
        #timestring = now.strftime("%x Last Updated: %I:%M %p")
        timestring = now.strftime("%x")
        self.im2.text((borderwidth+padding, padding+borderwidth), timestring, font=timefont, fill=(0, 0, 0))

        if self.badge_filename != "":
            try:
                vector_badge = svg2rlg(self.badge_filename)
                self.badge = renderPM.drawToPIL(vector_badge, dpi=100)
                self.badge = self.badge.convert("RGBA")
                aspect_ratio = self.badge.width / self.badge.height
            except Exception as e:
                print(f"unable to create badge from vector image {e}")

        if self.status != "Away":  
            #badge
            try:
                if self.badge.height > self.badge.width:
                    #portrait image. scale via height
                    max_logo_height = 190
                    self.badge = self.badge.resize((int(max_logo_height * aspect_ratio),max_logo_height))
                else:
                    #landscape image. scale via width
                    max_logo_width = 220
                    self.badge = self.badge.resize((max_logo_width,int(max_logo_width/aspect_ratio)))
            except:
                print("skipping badge")

            #dixon_logo = dixon_logo.resize((logo_height,int(logo_height/aspect_ratio)))
            #im2.bitmap((borderwidth+padding+380, borderwidth+padding), dixon_logo, fill="blue")
            badge_x_anchor = int(((((display_width)+530)/2))-(self.badge.width/2))
            bar_y_anchor = 240
            badge_y_anchor = int((bar_y_anchor/2)-(self.badge.height/2))
            self.im.paste(self.badge,(badge_x_anchor, badge_y_anchor))

            # name
            name_y_anchor = 70
            namefont = ImageFont.truetype('fonts/Inter_28pt-Bold.ttf', 95)
            self.im2.text((borderwidth+padding, name_y_anchor), self.name, font=namefont, fill=EPD_BLACK)

            # title
            title_y_anchor = 190
            titlefont = ImageFont.truetype('fonts/Inter_28pt-Regular.ttf', 29)
            self.im2.text((borderwidth+padding, title_y_anchor), self.title, font=titlefont, fill=EPD_BLUE)

            # bar
            #bar_y_anchor = 240
            self.im2.line([(borderwidth+padding, bar_y_anchor),(display_width-borderwidth-padding,bar_y_anchor)],fill=EPD_BLACK, width=20)

            if self.banner_text == "":
                # static status text
                static_status_y_anchor = 260
                statusfont = ImageFont.truetype('fonts/Inter_28pt-Regular.ttf', 35)
                self.im2.text((borderwidth+padding, static_status_y_anchor), "STATUS:", font=statusfont, fill=EPD_BLACK)
            
                status_y_anchor = 280
            else:
                static_status_y_anchor = 260

                self.status = self.banner_text

            # status
            status_y_anchor = 280
            statusfont2_size = 120
            #statusfont2 = ImageFont.truetype('Inter/static/Inter-Bold.ttf', statusfont2_size)
            #statuscolor = bordercolor
            #boundingbox = im2.textbbox((borderwidth+padding, status_y_anchor), status.upper(), font=statusfont2)
            #anchor = (display_width/2)-((boundingbox[2]-boundingbox[0])/2)
            #im2.text((anchor , status_y_anchor), "FRIDAY", font=statusfont2, fill=statuscolor)
            # Center and dynamically size the status text
            max_width = display_width - 2 * (borderwidth + padding)

            while True:
                statusfont2 = ImageFont.truetype('fonts/Inter_28pt-Bold.ttf', statusfont2_size)
                boundingbox = self.im2.textbbox((0, 0), self.status.upper(), font=statusfont2)
                #anchor = (display_width/2)-((boundingbox[2]-boundingbox[0])/2)
                text_width = boundingbox[2] - boundingbox[0]
                text_height = boundingbox[3] - boundingbox[1]
                if text_width <= max_width:
                    break
                statusfont2_size -= 1

            anchor_x = (display_width - text_width) / 2
            anchor_y = (status_y_anchor+(( display_height - status_y_anchor - borderwidth - padding)) / 2) - text_height
            self.im2.text((anchor_x, anchor_y), self.status.upper(), font=statusfont2, fill=statuscolor)

            # available
            #if(focus_event is not None):
            #    if(in_event):
            #        time_free_avail = focus_event.end.strftime("%I:%M %p")
            #    else:
            #        time_free_avail = focus_event.start.strftime("%I:%M %p")
            
            #    availablility_y_anchor = 420
            #    statusfont3 = ImageFont.truetype('Inter/static/Inter-Black.ttf', 35)
            #    available_string = ""
            #    if(status == "Available"):
            #        available_string = "AVAILABLE UNTIL:"
            #    else:
            #        available_string = "FREE AT:"

            #    im2.text((borderwidth+padding, availablility_y_anchor), available_string, font=statusfont, fill=EPD_BLACK)
            #    boundingbox = im2.textbbox((borderwidth+padding, availablility_y_anchor), available_string, font=statusfont)

            
            #    im2.text((boundingbox[2]+20, availablility_y_anchor), time_free_avail, font=statusfont3, fill=EPD_BLACK)
            #    boundingbox = im2.textbbox((boundingbox[2]+20, availablility_y_anchor), str(time_free_avail), font=statusfont3)

        else:
            logo_height = 600
            dixon_logo = dixon_logo.resize((logo_height,int(logo_height/aspect_ratio)))
            #im2.bitmap((borderwidth+padding+380, borderwidth+padding), dixon_logo, fill="blue")
            self.im.paste(dixon_logo,(0, 100),dixon_logo)
        