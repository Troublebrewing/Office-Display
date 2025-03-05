import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

import json

import asyncio
from bleak import BleakClient, BleakScanner

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
        self.root.geometry("1020x560")
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
        
        self.tabControl = ttk.Notebook(self.right_frame) 
        self.customize_tab = ttk.Frame(self.tabControl, style="Custom.TFrame")
        self.preview_tab = ttk.Frame(self.tabControl, style="Custom.TFrame")
        style = ttk.Style()
        style.configure("Custom.TFrame", background=bg_color)
         
        
        self.tabControl.add(self.customize_tab, text ='Customize') 
        self.tabControl.add(self.preview_tab, text ='Preview') 
        self.tabControl.pack(expand = 1) 

        # Canvas for displaying the selected image
        self.canvas = tk.Canvas(self.preview_tab, width=800, height=480, bg=bg_color)
        self.canvas.pack()

        # Buttons below the image
        self.control_frame = tk.Frame(self.right_frame, bg=bg_color)
        self.control_frame.pack(fill=tk.X)

        self.refresh_button = tk.Button(self.control_frame, text="Refresh")
        self.refresh_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.refresh_button.config(command=self.refresh)

        self.upload_button = tk.Button(self.control_frame, text="Upload")
        self.upload_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.dropdown_var = tk.StringVar(self.control_frame) 
        #self.dropdown_var.set("Option 1")  # default value

        self.dropdown_menu = ttk.Combobox(self.control_frame, textvariable=self.dropdown_var, state="readonly")
        self.dropdown_menu.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Load thumbnails and bind listbox selection
        #self.load_thumbnails()
        self.load_presets()

        
        # No address provided, scan for devices
        self.refresh()

        #test = preset1.Presetx(status="Available")
        #test = preset1.Presetx(name="Tyler Bules", title="Electrical Engineering Manager", status="Out")
        #test.im.show()
        #self.listbox.bind('<<ListboxSelect>>', self.on_thumbnail_select)

    def refresh(self):
        print("Refreshing...")
        asyncio.run(self.scan_for_devices())
        #asyncio.create_task(self.scan_for_devices())

    def _on_mouse_wheel(self, event):
        self.left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_presets(self):
        try:
            with open('presets.json', 'r') as file:
                presets_data = json.load(file)
        except Exception as e:
            print(f"Unable to open presets.json file: {e}")

        self.preset_list = []

        if presets_data is not None:
            for preset_info in presets_data['presets']:
                try:
                    module_name = preset_info['module']
                    class_name = module_name                    

                    #import module
                    module = __import__(module_name)
                    
                    #get class from module
                    preset_class = getattr(module, class_name)
                    
                    #create instance of class
                    preset_instance = preset_class()
                
                    #set fields from json data
                    for field in preset_class.fields:
                        if field in preset_info:
                            setattr(preset_instance, field, preset_info[field])

                    #render image
                    preset_instance.render()

                    #append image to list
                    self.preset_list.append(preset_instance)
                except Exception as e:
                    print(f"Error loading preset: {e}")

        for preset in self.preset_list:
            #render image
            preset.render()
            
            #img = Image.open(thumbnail_file)
            thumbnail_img = preset.im.copy()
            thumbnail_img.thumbnail((180, 200))
            thumbnail_img = ImageTk.PhotoImage(thumbnail_img)
            #self.image_list.append(img)
            #self.thumbnail_list.append(thumbnail_img)
            label = tk.Label(self.scrollable_frame, image=thumbnail_img, width=200, height=120, bg=bg_color)
            label.image = thumbnail_img
            label.pack(padx=0, pady=0)
            label.bind("<Button-1>", lambda e, preset=preset: [self.thumbnail_select(preset, self.change_bg_color(label))])
        
        # Update the scroll region after loading all thumbnails
        self.left_canvas.configure(scrollregion=self.scrollable_frame.bbox("all"))

    def thumbnail_select(self, preset, label):
        #render full size image into preview tab
        preset.render()
        img=ImageTk.PhotoImage(preset.im)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

        #erase all widgets in customize tab
        for widget in self.customize_tab.winfo_children():
            widget.destroy()

        #render configurable fields into customize tab
        #preset_fields = img.preset.fields
        preset_fields = ['name', 'title', 'badge', 'status', 'banner_text']
        for field in preset_fields:
            label = tk.Label(self.customize_tab, text=field, bg=bg_color, fg=fg_color)
            label.pack(anchor='w', padx=10, pady=5)
            entry = tk.Entry(self.customize_tab)
            entry.pack(anchor='w', padx=10, pady=5)
            #entry.insert(0, getattr(img.preset, field, ''))

    def change_bg_color(self, label):
        label.config(bg="white")
        label.update()

    # Define a function to scan for BLE devices
    async def scan_for_devices(self):
        try:
            print("Scanning for BLE devices...")
            devices = await BleakScanner.discover(timeout=5.0)
            print(f"Scan complete. Found {len(devices)} devices.")

            self.named_bt_devices_found = [device for device in devices if device.name]
            
            if not self.named_bt_devices_found:
                print("No devices with names found.")
                return None
            
            print("Available devices:")
            for i, device in enumerate(self.named_bt_devices_found):
                print(f"{i + 1}. {device.name} - {device.address}")
                self.dropdown_menu['values'] = [device.name for device in self.named_bt_devices_found]



        except Exception as e:
            print(f"Error during scan: {e}")
            return []

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()