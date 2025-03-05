#libraries for image compositing
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageTk

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
# UUIDs for the virtual serial port
SERVICE_UUID = "569a1101-b87f-490c-92cb-11ba5ea5167c"
TX_FIFO_UUID = "569a2000-b87f-490c-92cb-11ba5ea5167c"  # Transmit characteristic
RX_FIFO_UUID = "569a2001-b87f-490c-92cb-11ba5ea5167c"  # Receive characteristic

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

import tkinter as tk

REFRESH_PERIOD_MINUTES = 5

enable_serial = 1

def make_image(focus_event):
    in_event = In_event(focus_event)

    if(in_event):
        if(focus_event.summary == "Focus time"):
            status = "Focus"
        elif(focus_event.summary == "Out of office"):
            status = "Out of Office"
        else:
            status = "Busy"
    else:
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
    if (status == "Busy") or (status == "Out of Office"):
        bordercolor = EPD_RED
    if status == "Available":
        bordercolor = EPD_GREEN

    #outline
    borderwidth = 20
    padding = 10
    im2.rectangle([(0,0),(display_width-1,display_height-1)], fill=None, outline=bordercolor, width=borderwidth)

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

        banner_text = "Welcome Bob Grace"

        if banner_text == "":
            # static status text
            static_status_y_anchor = 260
            statusfont = ImageFont.truetype('Inter/static/Inter-Regular.ttf', 35)
            im2.text((borderwidth+padding, static_status_y_anchor), "STATUS:", font=statusfont, fill=EPD_BLACK)
        
            status_y_anchor = 280
        else:
            static_status_y_anchor = 260

            status = banner_text

        # status
        status_y_anchor = 280
        statusfont2_size = 120
        #statusfont2 = ImageFont.truetype('Inter/static/Inter-Bold.ttf', statusfont2_size)
        statuscolor = bordercolor
        #boundingbox = im2.textbbox((borderwidth+padding, status_y_anchor), status.upper(), font=statusfont2)
        #anchor = (display_width/2)-((boundingbox[2]-boundingbox[0])/2)
        #im2.text((anchor , status_y_anchor), "FRIDAY", font=statusfont2, fill=statuscolor)
        # Center and dynamically size the status text
        max_width = display_width - 2 * (borderwidth + padding)

        while True:
            statusfont2 = ImageFont.truetype('Inter/static/Inter-Bold.ttf', statusfont2_size)
            boundingbox = im2.textbbox((0, 0), status.upper(), font=statusfont2)
            #anchor = (display_width/2)-((boundingbox[2]-boundingbox[0])/2)
            text_width = boundingbox[2] - boundingbox[0]
            text_height = boundingbox[3] - boundingbox[1]
            if text_width <= max_width:
                break
            statusfont2_size -= 1

        anchor_x = (display_width - text_width) / 2
        anchor_y = (status_y_anchor+(( display_height - status_y_anchor - borderwidth - padding)) / 2) - text_height
        im2.text((anchor_x, anchor_y), status.upper(), font=statusfont2, fill=statuscolor)

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

    try:
        for event in todays_events:
            start_string = ""
            if(isinstance(event.start, datetime.date)):
                start_string = event.start.strftime("%Y-%m-%d")
            if(isinstance(event.start,datetime.datetime)):
                start_string = event.start.strftime("%Y-%m-%d %H:%M:%S")
            
            end_string = ""
            if(isinstance(event.end, datetime.date)):
                end_string = event.end.strftime("%Y-%m-%d")
            if(isinstance(event.end,datetime.datetime)):
                end_string = event.end.strftime("%Y-%m-%d %H:%M:%S")
            print(event.summary+" "+start_string+"-"+end_string)

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
    except:
        return focus_event
    
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

def run_length_encode(data):
    """
    Perform run-length encoding on a bytes or bytearray object.

    Parameters:
        data: A bytes or bytearray object to encode.

    Returns:
        A bytearray containing the run-length encoded data.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Input data must be of type bytes or bytearray")
    
    # Initialize an empty result list
    encoded = bytearray()

    # Handle the case of empty input
    if len(data) == 0:
        return encoded

    # Start the run-length encoding process
    count = 1
    prev_byte = data[0]

    for i in range(1, len(data)):
        current_byte = data[i]
        if current_byte == prev_byte:
            count += 1
            # Handle the case where count reaches the maximum value (255)
            if count == 256:
                encoded.append(prev_byte)
                encoded.append(count-1)                
                count = 1
        else:
            encoded.append(prev_byte)
            encoded.append(count)
            prev_byte = current_byte
            count = 1

    # Append the last run
    encoded.append(prev_byte)
    encoded.append(count)

    return encoded

def run_length_encode2(data):
    """
    Perform run-length encoding on a bytes or bytearray object.

    Parameters:
        data: A bytes or bytearray object to encode.

    Returns:
        A bytearray containing the run-length encoded data.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Input data must be of type bytes or bytearray")
    
    # Initialize an empty result list
    encoded = bytearray()

    # Handle the case of empty input
    if len(data) == 0:
        return encoded

    # Start the run-length encoding process
    encoded.append(data[0])
    count = 1
    i=1

    for i in range(1, len(data)):
        
        if(encoded[-1] == data[i]):
            #same byte, increment counter
            count += 1
            if(count == 256):
                #write count then the same character again
                encoded.append(count-1)
                count = 1
                encoded.append(encoded[-2])
        else:
            encoded.append(count)
            count = 1
            encoded.append(data[i])
    
    encoded.append(count)

    return encoded

def run_length_decode(data):
    # Initialize an empty result list
    decoded = bytearray()

    # Iterate over the encoded data two bytes at a time (count, value)
    i = 0
    while i < len(data):
        count = data[i + 1]     # First byte is the count
        value = data[i] # Second byte is the value
        decoded.extend([value] * count)  # Replicate 'value' by 'count' times
        i += 2

    return decoded

def review_image(image):
    """ Displays the image in a tkinter window with 'Update' and 'Skip' buttons """
    root = tk.Tk()
    root.title("Preview Image")

    img = ImageTk.PhotoImage(image)
    panel = tk.Label(root, image=img)
    panel.pack()

    result = asyncio.Future()

    def update():
        result.set_result("Update")
        root.destroy()

    def skip():
        result.set_result("Skip")
        root.destroy()

    btn_update = tk.Button(root, text="Update", command=update)
    btn_update.pack(side="left", padx=10)

    btn_skip = tk.Button(root, text="Skip", command=skip)
    btn_skip.pack(side="right", padx=10)

    root.mainloop()
    return result

def bytearray_compare(ba1, ba2):
    length1 = len(ba1)
    length2 = len(ba2)

    i = 0
    while(ba1[i] == ba2[i]):
        i = i+1
        if i==length1 or i==length2:
            break

    print(f"Mismatch found at index: {i}\n")
    print(f"bytearray1: {ba1[i-10:i+10]}")
    print(f"bytearray2: {ba2[i-10:i+10]}")

async def UpdateDisplay():
    #UpdateEventList()
    
    timestring = datetime.datetime.now().strftime("%I:%M %p")
    print(timestring+" Updating Display...")
    
    global focus_event
    global todays_events
    try:
        _focus_event = GetFocusEvent(todays_events)
    except:
        print("couldnt get focus event")
        _focus_event = []

    #check if focus event has changed
    if(focus_event != _focus_event):
        focus_event = _focus_event

        #update display when focus event will change
        #if In_event(focus_event):
        #    next_update_time = focus_event.end.strftime("%I:%M")
        #else:
        #    next_update_time = focus_event.start.strftime("%I:%M")
        #print(f"scheduling display update for {next_update_time}")
        #schedule.every.day.at(next_update_time).do(UpdateDisplay)

        try:
            print("New Focus Event:"+focus_event.summary)
        except:
            print("No focus event")        

        #create image to send
        im = make_image(focus_event)

        review_choice = await review_image(im)

        if review_choice == "Update":
            #encode into datastream for waveshare display
            wavesharebuf = epd.getbuffer(im)

            #image_bytes = bytes(wavesharebuf)
            image_bytearray = bytearray(wavesharebuf)
            #print(f"image bytes: {image_bytearray}\n")
            
            RLE_image_bytearray = run_length_encode2(image_bytearray)
            #RLE_image_bytearray = run_length_encode2(image_bytearray)
            #print(f"encoded image: {RLE_image_bytearray}\n")
            #bytearray_compare(RLE_image_bytearray, RLE_image_bytearray2)
            #decoded = run_length_decode(RLE_image_bytearray)
            #decoded2 = run_length_decode(RLE_image_bytearray2)
            #print(f'{decoded}')
            #print(f'{decoded2}')

            #bytearray_compare(image_bytearray, decoded)
            #bytearray_compare(image_bytearray, decoded2)

            #print(f"wavesharebuf size: {len(wavesharebuf)} RLE size: {len(RLE_wavesharebuf)}")
            #print(f"image_bytes size: {len(image_bytes)} RLE size: {len(RLE_image_bytes)}")
            print(f"image_bytearray size: {len(image_bytearray)} RLE size: {len(RLE_image_bytearray)}")

            #if(pcp):
            #if(test == 0):
            #print("Sending image through serial port...", end='')
            #pcp.write(wavesharebuf)
            #print("done")

            #device_connected=1
            #if(device_connected):

            #test = bytearray([255] * 510)
            #print(f"test length: {len(test)}\n")
            #print(f"test data: {test}\n")
            
            #encode_test = run_length_encode2(test)
            #print(f"encoded test length:{len(encode_test)}\n")
            #print(f"encoded test data: {encode_test}\n")

            #decode_test = run_length_decode(encode_test)
            #print(f"decoded test length:{len(decode_test)}\n")
            #print(f"decoded test: {decode_test}\n")
            await send_bytes_to_client(RLE_image_bytearray)
        else:
            print("User skipped update.")

        #show image
        #im.show()

        
        

        
    else:
        print(f"Focus event is still {focus_event.summary}. skipping...")

    #schedule next display update
    ScheduleNextUpdate(focus_event)    

    return schedule.CancelJob
    
def ScheduleNextUpdate(focus_event):
    in_event = In_event(focus_event)

    # available
    if(focus_event is not None):
        if(in_event):
            #next_time = focus_event.end.strftime("%I:%M %p")
            next_time = focus_event.end
        else:
            #next_time = focus_event.start.strftime("%I:%M %p")
            next_time = focus_event.start
    else:
        # Get the current time
        now = datetime.datetime.now()

        now_str = now.strftime('%H:%M')
    
        #print(f"runing run_once at: {now_str}")

        # Add the random number of minutes to the current time
        next_time = now + datetime.timedelta(minutes=5)

    # Print the time in HH:MM format
    next_time_str = next_time.strftime('%H:%M')

    print(f"next display update at: {next_time_str}")

    schedule.every().day.at(next_time_str).do(lambda: asyncio.ensure_future(UpdateDisplay))

    return schedule.CancelJob

def UpdateEventList():
    print("Fetching latest events...", end='')
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    global todays_events
    
    try:
        calendar = GoogleCalendar(credentials_path='.credentials/client_secret_107824529014-pggujlou2tr9hnva6oak0bf8o605lsll.apps.googleusercontent.com.json',default_calendar='tbules@dixonvalve.com', save_token=True, authentication_flow_port=8081)
        todays_events = list(calendar.get_events(time_min=datetime.datetime.now(), time_max=tomorrow_date))
        print("done")
    except Exception as e:
        print(f"failed{e}")

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
        devices = await BleakScanner.discover(timeout=5.0)
        print(f"Scan complete. Found {len(devices)} devices.")

        named_devices = [device for device in devices if device.name]
        
        if not named_devices:
            print("No devices with names found.")
            return None
        
        print("Available devices:")
        for i, device in enumerate(named_devices):
            print(f"{i + 1}. {device.name} - {device.address}")

        return named_devices

    except Exception as e:
        print(f"Error during scan: {e}")
        return []

# Callback to handle received notifications
def notification_handler(sender, data):
    """
    Callback function that is called when data is received from the Bluetooth device.
    
    Parameters:
        sender: The sender of the notification (characteristic UUID).
        data: The data received in bytes.
    """
    
    global response_received
    global bytes_received
    
    if b"rx:" in data:
        response_received = True
        bytes_received = int(data[3:].decode('ascii'), 16)
    else:
        print(f"Unexpected response from {sender}: {data}")

async def wait_for_response():
    """
    A helper function that waits for the response_received flag to be set to True.
    """
    global response_received
    while not response_received:
        await asyncio.sleep(0.01)  # Small sleep to avoid busy-waiting

# Define an async function to send a message to the device
async def send_bytes_to_client(databytes):
    global response_received
    global bytes_received

    max_retries = 5
    timeout_ms = 1000
    bytes_received = 0

    try:
        image_size = len(run_length_decode(databytes))
        # Check if the BleakClient object is available globally
        if "client" in globals():
            await client.connect()

            
            # Check if the client is connected
            if client.is_connected:
                await client.start_notify(TX_FIFO_UUID, notification_handler)

                print("Sending data to BLE Client")
                image_bytes_sent = 0
                #or i in range(0, len(databytes), 20):
                while bytes_received < len(databytes):
                    #chunk = databytes[i:i+20]
                    if bytes_received+20 < len(databytes):
                        chunk = databytes[bytes_received:bytes_received+20]
                    else:
                        chunk = databytes[bytes_received:]

                    decoded_chunk = run_length_decode(chunk)
                    image_bytes_sent = image_bytes_sent + len(decoded_chunk)
                    retries = 0 #initialize retries for each chunk

                    while retries < max_retries:
                        try:
                            # Wait for the acknowledgment before proceeding
                            response_received = False  # Reset flag before waiting
                                                        
                            # Send the message to the RXUUID of the Bluetooth device
                            await client.write_gatt_char(RX_FIFO_UUID, chunk)
                            
                            print(f"Transmitted: {bytes_received+len(chunk)}/{len(databytes)} bytes. Expanded: {image_bytes_sent}/{image_size}")
                            
                            try:
                                await asyncio.wait_for(wait_for_response(), timeout_ms / 1000)
                                if response_received:
                                    print(f"Client has received:{bytes_received} bytes")
                                    break
                            except asyncio.TimeoutError:
                                print(f"No response received within {timeout_ms}ms, retrying... (Attempt {retries+1}/{max_retries})")
                                retries += 1  # Increment retries if timeout occurs
                            
                        except Exception as e:
                            print(f"Error sending chunk: {e}")
                            retries += 1  # Increment retries on exception
                    
                    if retries == max_retries:
                        print(f"Max retries reached for chunk. Aborting.")
                        break

                print("Data transmission complete\n")

                # Stop notifications when done
                # await client.stop_notify(RX_FIFO_UUID)

                await client.disconnect()
                return  # Exit function after successful transmission

            else:
                print("Device is not connected.")

    except Exception as e:
        print(f"Error sending message to device: {e}")

async def connect_to_device(address=None):
    if address==None:
        # No address provided, scan for devices
        named_devices = await scan_for_devices()

        if not named_devices:
            return
    
        #prompt user for selection
        while True:
            try:
                selection = int(input("Enter the number of the device you wish to connect to: ")) - 1
                if 0 <= selection < len(named_devices):
                    selected_device = named_devices[selection]
                    address = selected_device.address
                    break                    
                else:
                    print("Invalid selection. Please choose a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    print(f"Attempting to connect to device at address {address}...")

    global client

    async with BleakClient(address) as client:
        if client.is_connected:
            print(f"Successfully connected to device at {address}")

            #global client
            #client = client_obj  # Save the BleakClient object globally

            # Write dummy bytes to the TX FIFO characteristic
            #dummy_data = bytearray([0x01, 0x02, 0x03, 0x04])  # Replace with actual data if needed
            #print(f"Sending dummy data: {dummy_data}")
            
            #try:
                #await client.write_gatt_char(TX_FIFO_UUID, dummy_data)
                #await client.write_gatt_char(RX_FIFO_UUID, dummy_data)
                #print(f"Data sent to TX FIFO characteristic ({RX_FIFO_UUID}).")
                
                #read_str = pcp.read(10)
                #print(f"serial data:{read_str}")
                # Optionally read from the RX FIFO after sending data
                #rx_data = await client.read_gatt_char(TX_FIFO_UUID)
                #print(f"Received data from RX FIFO characteristic: {rx_data}")
            #except Exception as e:
                #print(f"Failed to send or receive data: {e}")

        else:
            print(f"Failed to connect to device at {address}")

epd = epd7in3f.EPD()

utc = pytz.UTC
#pcp = serial.Serial('COM11', 115200, 8, "N", 1, timeout=10, rtscts=1)

async def main():
    #epd = epd7in3f.EPD()
    #utc = pytz.UTC

    #if(enable_serial == 1):      
    #    mystring = """AT+RUN "$autorun"\r\n"""
    #    pcp.write(mystring.encode())
    #    time.sleep(1)

    #to connect to a specific BT target, modify the address below
    await connect_to_device(address="FF:B2:EA:E5:D6:24")

    #if display address is unknown, dont specify address and it will scan and let you choose a device
    #await connect_to_device()
    
    global todays_events
    global focus_event

    #clear globals
    todays_events = []
    focus_event = []

    #fetch upcoming event list
    UpdateEventList()

    #initial update of display
    await UpdateDisplay()

    #periodically refresh event list
    #schedule.every(15).minutes.do(UpdateEventList)

    #periodically update display
    #schedule.every(2).minutes.do(UpdateDisplay)

    while(True):
        schedule.run_pending()
        time.sleep(1)

asyncio.run(main())

#schedule runs
#schedule.every(15).minutes.do(UpdateEventList)
#schedule.every(5).minutes.do(UpdateDisplay)

#schedule.every(30).seconds.do(UpdateEventList)
#schedule.every(1).minutes.do(UpdateDisplay)
#schedule.every().day.at("07:30").do(UpdateDisplay)  #start of day
#schedule.every().day.at("12:00").do(UpdateDisplay)  #lunch
#schedule.every().day.at("17:00").do(UpdateDisplay)  #end of day



