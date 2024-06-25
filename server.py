from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime
from pytz import timezone
import pytz
import serial

from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA

import epd7in3f
import time
import schedule

REFRESH_PERIOD_MINUTES = 5

def make_image(focus_event, in_event):
    
    if(in_event):
        if(focus_event.summary == "Focus time"):
            status = "Focus"
        else:
            status = "Busy"

    if(not in_event):
        status = "Available"
    
    display_width = 800
    display_height = 480

    im = Image.new(mode="RGB", size=(display_width,display_height), color="white")

    im2 = ImageDraw.Draw(im)
    im2.fontmode = "1"  #turns off text anti aliasing. quantization gets weird if this is on

    #colors
                 #0xBBGGRR
    EPD_BLACK   = 0x000000
    EPD_WHITE   = 0xFFFFFF
    EPD_GREEN   = 0x00FF00
    EPD_BLUE    = 0xFF0000
    EPD_RED     = 0x0000FF
    EPD_YELLOW  = 0x00FFFF
    EPD_ORANGE  = 0x007DFF
    
    bordercolor = "white"
    if status == "Focus":
        bordercolor = EPD_YELLOW
    if status == "Busy":
        bordercolor = EPD_RED
    if status == "Available":
        bordercolor = EPD_GREEN

    #outline
    borderwidth = 20
    padding = 10
    im2.rectangle([(0,0),(display_width,display_height)], fill=None, outline=bordercolor, width=borderwidth)

    # time
    timefont = ImageFont.truetype('Inter/static/Inter-Bold.ttf', 35)
    now = datetime.datetime.now()
    #print(now)
    #date
    #timestring = now.strftime("%x %I:%M %p")
    timestring = now.strftime("%x %I:%Mish")
    im2.text((borderwidth+padding, padding+borderwidth), timestring, font=timefont, fill=(0, 0, 0))

    # battery

    badge = Image.open("badge.png")
    aspect_ratio = badge.width / badge.height
    if status != "Away":  
        #badge
        if badge.height > badge.width:
            #portrait image. scale via height
            max_logo_height = 190
            badge = badge.resize((int(max_logo_height * aspect_ratio),max_logo_height))
        else:
            #landscape image. scale via width
            max_logo_width = 220
            badge = badge.resize((max_logo_width,int(max_logo_width/aspect_ratio)))

        #dixon_logo = dixon_logo.resize((logo_height,int(logo_height/aspect_ratio)))
        #im2.bitmap((borderwidth+padding+380, borderwidth+padding), dixon_logo, fill="blue")
        badge_x_anchor = int(((((display_width)+530)/2))-(badge.width/2))
        bar_y_anchor = 240
        badge_y_anchor = int((bar_y_anchor/2)-(badge.height/2))
        im.paste(badge,(badge_x_anchor, badge_y_anchor))

        # name
        name_y_anchor = 70
        namefont = ImageFont.truetype('Inter/static/Inter-Bold.ttf', 95)
        im2.text((borderwidth+padding, name_y_anchor), "Tyler Bules", font=namefont, fill=EPD_BLACK)

        # title
        title_y_anchor = 190
        titlefont = ImageFont.truetype('Inter/static/Inter-Regular.ttf', 29)
        im2.text((borderwidth+padding, title_y_anchor), "ELECTRICAL ENGINEERING MANAGER", font=titlefont, fill=EPD_BLUE)

        # bar
        #bar_y_anchor = 240
        im2.line([(borderwidth+padding, bar_y_anchor),(display_width-borderwidth-padding,bar_y_anchor)],fill=EPD_BLACK, width=20)

        # static status text
        static_status_y_anchor = 260
        statusfont = ImageFont.truetype('Inter/static/Inter-Regular.ttf', 35)
        im2.text((borderwidth+padding, static_status_y_anchor), "STATUS:", font=statusfont, fill=EPD_BLACK)

        # status
        status_y_anchor = 280
        statusfont2 = ImageFont.truetype('Inter/static/Inter-Bold.ttf', 120)
        statuscolor = bordercolor
        boundingbox = im2.textbbox((borderwidth+padding, status_y_anchor), status.upper(), font=statusfont2)
        anchor = (display_width/2)-((boundingbox[2]-boundingbox[0])/2)
        im2.text((anchor , status_y_anchor), status.upper(), font=statusfont2, fill=statuscolor)

        # available
        if(focus_event is not None):
            if(in_event):
                time_free_avail = focus_event.end.strftime("%I:%M %p")
            else:
                time_free_avail = focus_event.start.strftime("%I:%M %p")
        
            availablility_y_anchor = 420
            statusfont3 = ImageFont.truetype('Inter/static/Inter-Black.ttf', 35)
            available_string = ""
            if(status == "Available"):
                available_string = "AVAILABLE UNTIL:"
            else:
                available_string = "FREE AT:"

            im2.text((borderwidth+padding, availablility_y_anchor), available_string, font=statusfont, fill=EPD_BLACK)
            boundingbox = im2.textbbox((borderwidth+padding, availablility_y_anchor), available_string, font=statusfont)

        
            im2.text((boundingbox[2]+20, availablility_y_anchor), time_free_avail, font=statusfont3, fill=EPD_BLACK)
            boundingbox = im2.textbbox((boundingbox[2]+20, availablility_y_anchor), str(time_free_avail), font=statusfont3)

    else:
        logo_height = 600
        dixon_logo = dixon_logo.resize((logo_height,int(logo_height/aspect_ratio)))
        #im2.bitmap((borderwidth+padding+380, borderwidth+padding), dixon_logo, fill="blue")
        im.paste(dixon_logo,(0, 100),dixon_logo)

    return im

def GetFocusEvent(todays_events):
    #dummy_time_start = datetime.datetime.now() + datetime.timedelta(days=1)
    #dummy_time_end  = datetime.datetime.now() + datetime.timedelta(days=2)
    #focus_event = Event("Focus Event", start=dummy_time_start,end=dummy_time_end)

    focus_event = None

    for event in todays_events:
        #start_string = ""
        #if(isinstance(event.start, datetime.date)):
        #    start_string = event.start.strftime("%Y-%m-%d")
        #if(isinstance(event.start,datetime.datetime)):
        #    start_string = event.start.strftime("%Y-%m-%d %H:%M:%S")
        
        #end_string = ""
        #if(isinstance(event.end, datetime.date)):
        #    end_string = event.end.strftime("%Y-%m-%d")
        #if(isinstance(event.end,datetime.datetime)):
        #    end_string = event.end.strftime("%Y-%m-%d %H:%M:%S")
        #print(event.summary+" "+start_string+"-"+end_string)

        if(isinstance(event.start,datetime.datetime) & isinstance(event.end,datetime.datetime)):
            utcnow = datetime.datetime.now(datetime.UTC)
            now_local = utcnow.astimezone(timezone('US/Eastern'))
            
            if((now_local > event.start) & (now_local < event.end)):
                focus_event = event
                break

            if(event.start < focus_event.start):
                focus_event = event

    return focus_event

def In_event(event):
    in_event = False

    utcnow = datetime.datetime.now(datetime.UTC)
    now_local = utcnow.astimezone(timezone('US/Eastern'))
    
    try:
        if((now_local > event.start) & (now_local < event.end)):
            in_event = True 
    except:               
        return in_event
    return in_event

def UpdateDisplay():
    UpdateEvents()
    
    print("Updating Display...")
    
    #global todays_events
    global todays_events
    focus_event = GetFocusEvent(todays_events)
    
    try:
        print("Focus Event:"+focus_event.summary)
    except:
        print("No focus event")

    in_event = In_event(focus_event)

    im = make_image(focus_event, in_event)
    #im.show()
    wavesharebuf = epd.getbuffer(im)

    if(test == 0):
        print("Sending image through serial port...")
        pcp.write(wavesharebuf)
        print("done\n")


def UpdateEvents():
    print("Fetching latest events...")
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    global todays_events
    global calendar
    todays_events = calendar.get_events(time_min=datetime.datetime.now(), time_max=tomorrow_date)

from svglib.svglib import svg2rlg

import os
folder_path = os.path.abspath("./cairo/bin/")
path_env_var = os.environ["PATH"]
if folder_path not in path_env_var:
    os.environ["PATH"] = folder_path + os.pathsep + path_env_var

from reportlab.graphics import renderPM
import io

vector_badge = svg2rlg("badge.svg")
place_holder = io.BytesIO()
#renderPM.drawToFile(vector_badge, place_holder, fmt="PNG")
renderPM.drawToFile(vector_badge, "badge.png", fmt="PNG", dpi=100,)
#place_holder.show()

#import cairosvg 
#cairosvg.svg2png(file_obj=open("/badge.svg",'r'),output_width=200, write_to="badge.png")

epd = epd7in3f.EPD()

pcp = serial.Serial('COM5', 115200, 8, "N", 1, timeout=10, rtscts=1)

test = 0
if(test == 0):
    mystring = """AT+RUN "$autorun"\r\n"""
    pcp.write(mystring.encode())
    time.sleep(1)

calendar = GoogleCalendar('tbules@dixonvalve.com', save_token=True, authentication_flow_port=8081)

utc = pytz.UTC

#UpdateEvents()
UpdateDisplay()

#schedule.every(15).minutes.do(UpdateEvents)
schedule.every(5).minutes.do(UpdateDisplay)

while(True):
    schedule.run_pending()
    time.sleep(1)