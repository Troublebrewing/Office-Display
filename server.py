from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import datetime
import serial

from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, DAILY, SU, SA

status = "Available"
display_width = 800
display_height = 480

im = Image.new(mode="RGB", size=(display_width,display_height), color="white")

im2 = ImageDraw.Draw(im)

#colors
bordercolor = "white"
if status == "Focus":
    bordercolor = "yellow"
if status == "Busy":
    bordercolor = "red"
if status == "Available":
    bordercolor = "green"

#outline
borderwidth = 20
padding = 10
im2.rectangle([(0,0),(display_width,display_height)], fill=None, outline=bordercolor, width=borderwidth)

# time
timefont = ImageFont.truetype('Inter/static/Inter-Bold.ttf', 35)
now = datetime.datetime.now()
print(now)
im2.text((borderwidth+padding, padding+borderwidth), now.strftime("%x %I:%M %p"), font=timefont, fill=(0, 0, 0))

# battery

#dixon logo
dixon_logo = Image.open("Dixon Logo.png")
aspect_ratio = dixon_logo.width / dixon_logo.height
if status != "Away":    
    logo_height = 220
    dixon_logo = dixon_logo.resize((logo_height,int(logo_height/aspect_ratio)))
    #im2.bitmap((borderwidth+padding+380, borderwidth+padding), dixon_logo, fill="blue")
    im.paste(dixon_logo,(borderwidth+padding+510, borderwidth+padding),dixon_logo)

    # name
    name_y_anchor = 70
    namefont = ImageFont.truetype('Inter/static/Inter-Bold.ttf', 95)
    im2.text((borderwidth+padding, name_y_anchor), "Tyler Bules", font=namefont, fill=(0, 0, 0))

    # title
    title_y_anchor = 190
    titlefont = ImageFont.truetype('Inter/static/Inter-Regular.ttf', 29)
    im2.text((borderwidth+padding, title_y_anchor), "ELECTRICAL ENGINEERING MANAGER", font=titlefont, fill=(0, 0, 255))

    # bar
    bar_y_anchor = 240
    im2.line([(borderwidth+padding, bar_y_anchor),(display_width-borderwidth-padding,bar_y_anchor)],fill='black', width=20)

    # static status text
    static_status_y_anchor = 260
    statusfont = ImageFont.truetype('Inter/static/Inter-Regular.ttf', 35)
    im2.text((borderwidth+padding, static_status_y_anchor), "STATUS:", font=statusfont, fill=(0, 0, 0))

    # status
    status_y_anchor = 280
    statusfont2 = ImageFont.truetype('Inter/static/Inter-Bold.ttf', 120)
    statuscolor = bordercolor
    boundingbox = im2.textbbox((borderwidth+padding, status_y_anchor), status.upper(), font=statusfont2)
    anchor = (display_width/2)-((boundingbox[2]-boundingbox[0])/2)
    im2.text((anchor , status_y_anchor), status.upper(), font=statusfont2, fill=statuscolor)

    # available
    time_until_free = 27
    availablility_y_anchor = 420
    statusfont3 = ImageFont.truetype('Inter/static/Inter-Black.ttf', 35)
    im2.text((borderwidth+padding, availablility_y_anchor), "AVAILABLE IN:", font=statusfont, fill=(0, 0, 0))

    im2.text((borderwidth+270, availablility_y_anchor), str(time_until_free), font=statusfont3, fill=(0, 0, 0))
    boundingbox = im2.textbbox((borderwidth+padding+260, availablility_y_anchor), str(time_until_free), font=statusfont3)

    anchor = boundingbox[2]+padding
    im2.text((anchor, availablility_y_anchor), "MINUTES", font=statusfont3, fill=(0, 0, 0))

else:
    logo_height = 600
    dixon_logo = dixon_logo.resize((logo_height,int(logo_height/aspect_ratio)))
    #im2.bitmap((borderwidth+padding+380, borderwidth+padding), dixon_logo, fill="blue")
    im.paste(dixon_logo,(0, 100),dixon_logo)

waveshare_pallete = [0,0,0,255,255,255,0,128,0,0,0,255,255,0,0,255,255,0,255,170,0]
waveshare_pallete2 = [
    0x000000,  # Black
    0xFFFFFF,  # White
    0x00FF00,  # Green
    0x0000FF,  # Blue
    0xFF0000,  # Red
    0xFFFF00,  # Yellow
    0xFF7D00,  # Orange
]
arbitrary_size = 16, 16
palimage = Image.new('P', arbitrary_size)
palimage.putpalette(waveshare_pallete)

im.quantize(palette=palimage)

#calendar = GoogleCalendar('tbules@dixonvalve.com')
#for event in calendar.get_events():
#    print(event)

#im.show()

pcp = serial.Serial('COM5', 115200, 8, "N", 1, timeout=10)

#pcp.dtr(0)
mystring = """AT+RUN "$autorun"\r\n"""
pcp.write(mystring.encode())

response = pcp.read(100)

response_char = response.decode()

print(response_char)
