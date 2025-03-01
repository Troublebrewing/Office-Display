import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import preset1

theme = "dark"

if theme == "dark":
    bg_color = '#333'
    fg_color = '#fff'
if theme == "light":
    bg_color = '#fff'
    fg_color = '#000'

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1020x530")
        self.root.resizable(False, False)
        self.root.title("Image Viewer")

        # Left frame for presets
        self.left_frame = tk.Frame(root, bg=bg_color) #frame will grow or shrink to size of widgets within frame
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        #the word preset
        self.preset_label = tk.Label(self.left_frame, text="Presets:", bg=bg_color, fg=fg_color, font=("Helvetica", 10, "bold"))
        self.preset_label.pack(fill=tk.X, expand=True)

        # Scrollbar for presets
        self.left_canvas = tk.Canvas(self.left_frame, width=200, height=530, bg=bg_color)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.left_canvas.yview)
        self.scrollbar.configure(style="Vertical.TScrollbar")
        style = ttk.Style()
        style.configure("Vertical.TScrollbar", background=bg_color)
        self.scrollable_frame = tk.Frame(self.left_canvas, width=200, height=530, bg=bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.left_canvas.configure(
                scrollregion=self.left_canvas.bbox("all")
            )
        )

        self.left_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.left_canvas.configure(yscrollcommand=self.scrollbar.set)

        #self.left_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind the mouse wheel to the canvas
        self.left_canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)
        
        # Right frame for image display and buttons
        self.right_frame = tk.Frame(root, width=800, height=480, bg=bg_color)
        #self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right_frame.pack(side=tk.RIGHT)
        
        # Canvas for displaying the selected image
        self.canvas = tk.Canvas(self.right_frame, width=800, height=480, bg=bg_color)
        self.canvas.pack()

        # Buttons below the image
        self.button_frame = tk.Frame(self.right_frame, bg=bg_color)
        self.button_frame.pack(fill=tk.X)

        self.button1 = tk.Button(self.button_frame, text="Refresh")
        self.button1.pack(side=tk.LEFT, padx=10, pady=10)

        self.button2 = tk.Button(self.button_frame, text="Upload")
        self.button2.pack(side=tk.RIGHT, padx=10, pady=10)

        # Load thumbnails and bind listbox selection
        #self.load_thumbnails()
        self.load_presets()

        #test = preset1.Presetx(status="Available")
        #test = preset1.Presetx(name="Tyler Bules", title="Electrical Engineering Manager", status="Out")
        #test.im.show()
        #self.listbox.bind('<<ListboxSelect>>', self.on_thumbnail_select)

    def _on_mouse_wheel(self, event):
        self.left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_thumbnails(self):
        self.image_list = []
        self.thumbnail_list = []

        self.preset_thumbnail_filenames = ["thumb1.bmp", "thumb2.bmp", "thumb3.bmp","thumb1.bmp", "thumb2.bmp", "thumb3.bmp","thumb1.bmp", "thumb2.bmp", "thumb3.bmp","thumb1.bmp", "thumb2.bmp", "thumb3.bmp"]
        
        for thumbnail_file in self.preset_thumbnail_filenames:
            img = Image.open(thumbnail_file)
            thumbnail_img = img.copy()
            thumbnail_img.thumbnail((180, 200))
            thumbnail_img = ImageTk.PhotoImage(thumbnail_img)
            #self.image_list.append(img)
            self.thumbnail_list.append(thumbnail_img)
            label = tk.Label(self.scrollable_frame, image=thumbnail_img)
            label.image = thumbnail_img
            label.pack(padx=10, pady=10)
            label.bind("<Button-1>", lambda e, img=img: self.display_image(ImageTk.PhotoImage(img)))
        
        # Update the scroll region after loading all thumbnails
        self.left_canvas.configure(scrollregion=self.scrollable_frame.bbox("all"))

    def load_presets(self):
        self.preset_list = []

        p1 = preset1.Presetx(status="Available")
        p2 = preset1.Presetx(name="Tyler Bules", status="Available")
        p3 = preset1.Presetx(status="Away2")
        p4 = preset1.Presetx(title="buttsniffer", status="Available")
        p5 = preset1.Presetx(status="Out of Office")
        p6 = preset1.Presetx(name="King Arthur", title="fastest kid alive", status="Available")

        self.preset_list.append(p1.im)
        self.preset_list.append(p2.im)
        self.preset_list.append(p3.im)
        self.preset_list.append(p4.im)
        self.preset_list.append(p5.im)
        self.preset_list.append(p6.im)

        for preset in self.preset_list:
            #img = Image.open(thumbnail_file)
            thumbnail_img = preset.copy()
            thumbnail_img.thumbnail((180, 200))
            thumbnail_img = ImageTk.PhotoImage(thumbnail_img)
            #self.image_list.append(img)
            #self.thumbnail_list.append(thumbnail_img)
            label = tk.Label(self.scrollable_frame, image=thumbnail_img)
            label.image = thumbnail_img
            label.pack(padx=10, pady=10)
            label.bind("<Button-1>", lambda e, img=preset: self.display_image(ImageTk.PhotoImage(preset)))
        
        # Update the scroll region after loading all thumbnails
        self.left_canvas.configure(scrollregion=self.scrollable_frame.bbox("all"))

    def display_image(self, img):
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()