import tkinter as tk
from tkinter import ttk
import customtkinter
from PIL import Image, ImageTk

import json

import asyncio
import threading
from bleak import BleakClient, BleakScanner

class PresetListFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)        
        self.title = "Presets"    

        #self.configure(fg_color="red")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        #self.root = root
        self.geometry("1020x560")        
        self.title("Epaper Display Manager")
        self.grid_columnconfigure(0, weight=1, uniform="group1")
        self.grid_columnconfigure(1, weight=4, uniform="group1")
        self.grid_rowconfigure(1, weight=1)
        self.maxsize(1020,560)

        # add widgets onto the frame...
        self.label = customtkinter.CTkLabel(self, text="Presets:")
        self.label.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        
        # Left frame for presets
        self.preset_list_frame = PresetListFrame(self) #frame will grow or shrink to size of widgets within frame
        self.preset_list_frame.grid(row=1, column=0, ipadx=0, padx=0, pady=0, sticky="nsew")
        
        # Right frame for image display and buttons
        self.right_frame = customtkinter.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=0, pady=0, rowspan=2, sticky="nsew")
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)
        
        self.tabControl = customtkinter.CTkTabview(self.right_frame) 
        self.tabControl.add("Customize")
        self.tabControl.add("Preview")
        self.tabControl.set("Preview")
        self.tabControl.grid(row=0, column=0, padx=0, pady=0, sticky="nsew") 

        # Canvas for displaying the selected image
        self.canvas = tk.Canvas(self.tabControl.tab("Preview"), width=800, height=480)
        self.canvas.pack()

        # Buttons below the image
        self.control_frame = customtkinter.CTkFrame(self.right_frame, fg_color="transparent")
        self.control_frame.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        self.refresh_button = customtkinter.CTkButton(self.control_frame, text="Refresh", command=self.refresh)
        self.refresh_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.upload_button = customtkinter.CTkButton(self.control_frame, text="Upload", command=self.upload)
        self.upload_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.selected_bt_device = customtkinter.StringVar(self.control_frame) 
        #self.dropdown_var.set("Option 1")  # default value

        self.dropdown_menu = customtkinter.CTkComboBox(self.control_frame, variable=self.selected_bt_device, state="readonly")
        self.dropdown_menu.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Load thumbnails and bind listbox selection        
        self.load_presets()

        self.draw_ui_preset_list()

        self.selected_preset = self.preset_list[0]
        
        # Start the asyncio event loop integration
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.run_event_loop, daemon=True).start()
        
        # No address provided, scan for devices
        self.refresh()

        

        #test = preset1.Presetx(status="Available")
        #test = preset1.Presetx(name="Tyler Bules", title="Electrical Engineering Manager", status="Out")
        #test.im.show()
        #self.listbox.bind('<<ListboxSelect>>', self.on_thumbnail_select)

    def upload(self):
        print("Uploading...")
        self.selected_bt_device

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

            self.selected_preset = self.preset_list[0]

    def draw_ui_preset_list(self):
        #for widget in self.preset_list_frame.winfo_children():
        #    widget.destroy()

        left_frame_width = self.preset_list_frame.cget("width")

        padding = 20

        for preset in self.preset_list:
            #render image
            preset.render()
            
            #img = Image.open(thumbnail_file)
            thumbnail_img = preset.im.copy()
            thumbnail_img.thumbnail((left_frame_width-(2*padding), left_frame_width-(2*padding)))
            thumbnail_img = ImageTk.PhotoImage(thumbnail_img)
            #self.image_list.append(img)
            #self.thumbnail_list.append(thumbnail_img)
            label = customtkinter.CTkLabel(self.preset_list_frame, image=thumbnail_img, compound="top", width=left_frame_width, height=120, padx=10, pady=0)
            if preset == self.selected_preset:
                label.configure(fg_color="red")
            label.image = thumbnail_img
            label.preset = preset
            label.pack(side= tk.TOP, fill=tk.X, expand=True)
            #label.bind("<Button-1>", lambda e, preset=preset: [self.thumbnail_select(preset, self.change_bg_color(label))])
            label.bind("<Button-1>", command=self.thumbnail_select)
        
        # Update the scroll region after loading all thumbnails
        #self.preset_list_frame.configure(scrollregion=self.scrollable_frame.bbox("all"))

    def thumbnail_select(self, event):        
        #find the index of previously selected preset
        selected_index = self.preset_list.index(self.selected_preset)

        #set fg color of previously selected widget to transparent
        self.preset_list_frame.winfo_children()[selected_index].configure(fg_color='transparent')

        #set fg color of selected widget to highlight it
        event.widget.master.configure(fg_color="red")

        #set new selected preset
        self.selected_preset = event.widget.master.preset

        #render full size image into preview tab
        self.selected_preset.render()
        img=ImageTk.PhotoImage(self.selected_preset.im)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

        #erase all widgets in customize tab
        #for widget in self.tabControl.tab("Customize").winfo_children():
        #    widget.destroy()

        #render configurable fields into customize tab
        #preset_fields = img.preset.fields
        #preset_fields = ['name', 'title', 'badge', 'status', 'banner_text']
        #for field in preset_fields:
        #    label = customtkinter.CTkLabel(self.tabControl.tab("Customize"), text=field)
        #    label.pack(anchor='w', padx=10, pady=5)
        #    entry = customtkinter.CTkEntry(self.tabControl.tab("Customize"))
        #    entry.pack(anchor='w', padx=10, pady=5)
            #entry.insert(0, getattr(img.preset, field, ''))

    def refresh(self):
        print("Refreshing...")
        asyncio.run_coroutine_threadsafe(self.scan_for_devices(), self.loop)
        #asyncio.run(self.scan_for_devices())

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
                self.dropdown_menu.configure(values = [device.name for device in self.named_bt_devices_found])



        except Exception as e:
            print(f"Error during scan: {e}")
            return []
        
    def run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    #def start_async_task(self):
        #asyncio.run_coroutine_threadsafe(self.handle_async_task(), self.loop)
    
    #async def handle_async_task(self):
        #self.label.configure(text="Running...")
        #result = await self.async_task()
        #self.label.configure(text=result)
        

if __name__ == "__main__":
    #root = tk.Tk()
    app = App()
    #asyncio.run(app.refresh())
    app.mainloop()