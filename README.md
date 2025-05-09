# Project
Office-Display is a customizable e-ink display system designed for office or desk environments. It allows users to compose and transfer content to an e-ink screen using a companion PC application. The project includes firmware for the display device, hardware driver board for the display, and a desktop application to composite and transfer information to be shown on the display. Whether you want to display your schedule, to-do list, inspirational quotes, or custom graphics, Office-Display provides a flexible and power-efficient solution. The device works using bluetooth low-energy BLE and an e-ink display so it can operate for months on a single battery.
![IMG_7800](https://github.com/user-attachments/assets/54cef6d4-da48-4519-96c5-ae89816d3c46)

# Usage

# Architecture
## Display firmware
`$autorun$.sign.sb` is a Laird/Ezurio Smartbasic application that advertises, receives connections, receives and uncompresses the data, then sends it to the display.

## PC Server application & Preset Management
The PC Server application `server.py` is the central tool for managing and deploying content to the e-ink display. It allows users to browse a list of presets, which are reusable layouts or scenes, preview the preset, and send it to the a display. This makes it easy to switch between different types of content—such as a daily schedule, a welcome message, or a quote of the day—with minimal effort.
![2025-05-09_9-18-08](https://github.com/user-attachments/assets/3b083b7a-b42b-42c6-b349-94c692839384)

### Template System
Each preset is based on a template, which is a Python script that defines:
 - Layout structure – specifying where each element (text, image, etc.) should be placed on the canvas.
 - Placeholder content – defining which parts of the layout are dynamic and can be filled in with different data for each preset.
 - Element types – supporting text fields, shapes, raster images (e.g., PNGs), and vector graphics (e.g., SVGs).

Templates serve as blueprints for visual compositions. For example, a "Meeting Room Schedule" template might include placeholder fields for room name, time slots, and occupancy status, with fixed styling and layout constraints.

### preset.json
All instances of templates—i.e., the actual content to be displayed—are stored in a JSON file called preset.json. This file contains:

 - Template references – linking each preset to its corresponding Python template.
 - Substitutions – specifying the actual text or data that should replace placeholders in the template.
 - Image references – pointing to local raster/vector image files that should be embedded in the rendered display output.
 - Rendering parameters – such as update frequency, rotation, or custom behaviors (planned for future support).

This system enables a clean separation between layout logic (in Python templates) and content data (in preset.json).

### Current Workflow
At present, users must manually edit preset.json to:
 - Add a new preset
 - Update content or images in an existing preset
 - Delete a preset

While this gives users full control and transparency over the structure of their display content, it does require some technical familiarity with JSON and the file structure of the project.

### Planned Improvements
A GUI-based preset editor is planned for future development. This will make the system much more user-friendly and accessible to non-technical users, transforming the Office-Display into a plug-and-play solution for everyday office or home use.

## Communication
At transfer time, the image is reduced to the 7 color colorspace which the e-ink display uses, then packed into the byte array it expects. The 
   
