#libraries for image compositing
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#library to pack image data for waveshare display
#this is from the rpi library from the display manufacturer
import epd7in3f

#libraries for various time functions
import datetime
from pytz import timezone
import pytz
import time
import schedule

#libraries for retrieving google calendar
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA

import asyncio
from bleak import BleakClient, BleakScanner
import serial

#cairo has some external dependencies
import os
folder_path = os.path.abspath("./cairo/bin/")
path_env_var = os.environ["PATH"]
if folder_path not in path_env_var:
    os.environ["PATH"] = folder_path + os.pathsep + path_env_var

#import these libraries for svg conversion
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

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

    #colors      #0xBBGGRR
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
    #timestring = now.strftime("%x Last Updated: %I:%M %p")
    timestring = now.strftime("%x")
    im2.text((borderwidth+padding, padding+borderwidth), timestring, font=timefont, fill=(0, 0, 0))

    # battery

    try:
        vector_badge = svg2rlg("badge.svg")
        renderPM.drawToFile(vector_badge, "badge.png", fmt="PNG", dpi=100)
    except:
        print("unable to create badge from vector image")

    try:
        badge = Image.open("badge.png")
        aspect_ratio = badge.width / badge.height
    except:
        print("no badge image file found")
    
    if status != "Away":  
        #badge
        try:
            if badge.height > badge.width:
                #portrait image. scale via height
                max_logo_height = 190
                badge = badge.resize((int(max_logo_height * aspect_ratio),max_logo_height))
            else:
                #landscape image. scale via width
                max_logo_width = 220
                badge = badge.resize((max_logo_width,int(max_logo_width/aspect_ratio)))
        except:
            print("skipping badge")

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
            if focus_event is None:
                focus_event = event

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
    UpdateEventList()
    
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


def UpdateEventList():
    print("Fetching latest events...")
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    global todays_events
    
    try:
        calendar = GoogleCalendar('tbules@dixonvalve.com', save_token=False, authentication_flow_port=8081)
        todays_events = list(calendar.get_events(time_min=datetime.datetime.now(), time_max=tomorrow_date))
    except Exception as e:
        print(f"unable to fetch events: {e}")
        
# Define a class to represent a BLE device
class Device:
    def __init__(self, name, address, services):
        self.name = name
        self.address = address
        self.services = services

# Define a function to scan for BLE devices
async def scan_for_devices():
    devices_found = []
    try:
        print("Scanning for BLE devices...")
        devices = await BleakScanner.discover()
        print(f"Found {len(devices)} devices.")

        for device in devices:
            if str(device.name) != "None":
                services = device.metadata.get("uuids", [])
                devices_found.append(
                    Device(
                        str(device.name + "\n" + device.address),
                        str(device.address),
                        services,
                    )
                )

        print("Scan complete.")
        return devices_found

    except Exception as e:
        print(f"Error during scan: {e}")
        return []

# Define an async function to send a message to the device
async def send_message_to_device(message):
    try:
        # Check message length
        if len(message) <= 20:
            # Pad spaces if message is shorter than 20 bytes
            message = message.ljust(20)
            # Check if the BleakClient object is available globally
            if "client" in globals():
                # Check if the client is connected
                if client.is_connected:
                    # Encode the message string to bytes before sending
                    message_bytes = message.encode()
                    # Send the message to the RXUUID of the Bluetooth device
                    await client.write_gatt_char(
                        RX_UUID, message_bytes, response=True
                    )
                    return  # Exit function after successful transmission
                else:
                    print("Device is not connected.")
                    open_dlg_modal()
                    page.update()

            else:
                print("BleakClient object not available.")
        else:
            # Print error message to chat log under system user
            error_message = Message(
                "System",
                "Error: Message cannot exceed 20 bytes",
                message_type="system_message",
            )
            chat.controls.append(ChatMessage(error_message))
            page.update()
            print("Error: Message cannot exceed 20 bytes.")
    except Exception as e:
        print(f"Error sending message to device: {e}")
        open_dlg_modal()
        page.update()

epd = epd7in3f.EPD()

pcp = serial.Serial('COM5', 115200, 8, "N", 1, timeout=10, rtscts=1)

test = 0
if(test == 0):
    mystring = """AT+RUN "$autorun"\r\n"""
    pcp.write(mystring.encode())
    time.sleep(1)


utc = pytz.UTC

#UpdateEventList()
UpdateDisplay()

#schedule.every(15).minutes.do(UpdateEventList)
schedule.every(5).minutes.do(UpdateDisplay)

while(True):
    schedule.run_pending()
    time.sleep(1)