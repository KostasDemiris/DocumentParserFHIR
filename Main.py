import os

import keyboard
import subprocess
import time

from pynput import keyboard
from pynput import mouse

# Ignore the errors, this does actually work
from Quartz.CoreGraphics import CGDisplayBounds
from Quartz.CoreGraphics import CGMainDisplayID

import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk, ImageGrab
import os
import ironpdf



# noinspection PyMethodMayBeStatic
# -- This is because it was annoying me
class systemInteractions:
    def __init__(self):
        self.__brew_dependencies = []
        self.dependencies_installed = self.install_dependencies(self.__brew_dependencies)
        self.__QuartzMonitorObj = CGDisplayBounds(CGMainDisplayID)

    def get_screen_size(self):
        return [self.__QuartzMonitorObj.width, self.__QuartzMonitorObj.height]

    def run_command(self, command, isGlobal=False):
        if isGlobal:
            try:
                subprocess.run(args=["cd"])
            except subprocess.CalledProcessError as e:
                print("Couldn't enter global scope, executing in local directory instead")
        try:
            return subprocess.run(args=command, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            raise e
            # returns the exception up for the code that ran the command to deal with right now
            # Could be modified to deal with exception internally

    def import_modules(self):
        try:
            import time
            import os
        except ImportError as e:
            print(f"uh oh, {e} just happened")

        # For modules that are not installed by default
        try:
            import keyboard
        except ImportError as e:
            self.run_command(["pip", "install", "keyboard"])
            import keyboard

        try:
            import pynput
            from pynput import mouse
            from pynput import keyboard
            from pynput.keyboard import Controller

        except ImportError as e:
            self.run_command(["pip", "install", "pynput"])
            import pynput
            from pynput import mouse
            from pynput import keyboard
            from pynput.keyboard import Controller, Listener

    def install_dependencies(self, brew_dependencies):
        failed = []

        self.import_modules()

        for dependency in brew_dependencies:
            try:
                self.run_command(["brew", "install", dependency])

            except subprocess.CalledProcessError as e:
                print(f"Installation of dependency {dependency} failed")
                failed.append([dependency, e])
                # Add code to deal with this in more detail later

        if failed:
            return False
        return True

    def quit(self, message):
        raise SystemExit(message)


class settings:
    # A settings object that any object with updatable settings should be able to access
    # It contains all the changeable values that a user should be able to modify
    def __init__(self, settings_file_path):
        if settings_file_path is None:
            # These are the defaults if no settings are provided
            self.__start_recording_key = '<cmd>+<shift>+e'
            self.__quit_thread_key = '<cmd>+<shift>+m'
            # As much as we could change this to an array, we have a fixed number of them and this is more readable
            self.__recording_period = 5.0

        else:
            self.__start_recording_key, self.__quit_thread_key, self.__recording_period = \
                self.get_settings(self.__path)

    def get_settings(self, path):
        pass

    def change_settings(self, path):
        pass

    def update_path(self, new_settings_path):
        self.__path = new_settings_path

    def get_keys(self):
        return self.__start_recording_key, self.__quit_thread_key

    def get_recording_period(self):
        return self.__recording_period


class finalityException(Exception):
    pass


class user_interaction:
    def __init__(self, settings_file_path):
        self.start_recording_key = '<cmd>+<shift>+1'
        self.quit_thread_key = '<cmd>+<shift>+2'
        self.stop_hotkeys_key = '<shift>+<cmd>+2'
        self.hotkeys = self.get_hot_keys()
        self.mouseTrackObj = None
        self.settings = settings(settings_file_path)
        self.systemInteractions = systemInteractions()
        self.rectangles_selected = []
        self.application_boundaries = [[0,0], [0,0]]
        # Not currently in use, but could bound mouse to the bounds of the application

    def get_hot_keys(self):
        return {self.start_recording_key: self.activate_recording,
        self.quit_thread_key: self.quit_thread,
        self.stop_hotkeys_key: self.stop_hotkeys}

    def start_up_mouse_tracking(self):
        self.mouseTrackObj = mouseTracker(self.settings)

    def activate_recording(self):
        print("Started recording")

        if self.mouseTrackObj is None:
            self.start_up_mouse_tracking()

        else:
            mouseRect = self.mouseTrackObj.select_rectangle()
            print(mouseRect)
            self.rectangles_selected.append(mouseRect)
            return mouseRect

    def stop_hotkeys(self):
        return False

    def quit_thread(self):
        print("Thread stopped")
        self.systemInteractions.quit(f"The quit hotkey ({self.quit_thread_key}) has been pressed")

    def keyTrackers(self):
        hotkeys = keyboard.GlobalHotKeys(self.hotkeys)
        hotkeys.start()

        # This is a blocking version
        # with keyboard.GlobalHotKeys(self.hotkeys) as hotkeys:
        #     hotkeys.join()


class mouseTracker:
    def __init__(self, settingsObj):
        self.settings_obj = settingsObj
        self.rectangle = []
        self.controller = mouse.Controller()


    def reset(self):
        # Resets the state before the tracker gets a rectangle
        self.rectangle = []

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            # Pressed down
            self.rectangle.append([x, y])
        elif button == mouse.Button.left:
            # Released
            self.rectangle.append([x, y])
            return False

    def return_last_rectangle(self):
        return sorted(self.rectangle, key=lambda point: [point[1], point[0]])

    def select_rectangle(self, bounds):
        self.reset()
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()
        return self.return_last_rectangle()


# userInt = user_interaction(None)
# userInt.keyTrackers()
# while True:
#     print("Main loop is going on")
#     time.sleep(5)


class front_end:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reading Application")

        self.current_pdf_path = None
        self.image_paths = []
        self.current_page = 0
        
        self.user_keylogger = user_interaction(None)

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="PDF Reading Application", font=("Georgia", 16))
        self.label.pack(pady=10)

        self.select_button = tk.Button(self.root, text="Select PDF", command=self.select_pdf)
        self.select_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.prev_button = tk.Button(self.root, text="Previous Page", command=self.turn_page_back,
                                     state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Can't be selected until the pdf has been selected

        self.next_button = tk.Button(self.root, text="Next Page", command=self.turn_page_forward, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.goto_button = tk.Button(self.root, text="Go to Page", command=self.turn_to_specific_page, state=tk.DISABLED)
        self.goto_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.save_button = tk.Button(self.root, text="Save Selected", command=self.get_last_rectangle)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)


        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        

    def convert_pdf_to_images(self, pdf_file):
        # For big PDF's, this can lag a lot. Ps got this from some tutorial
        pdf = ironpdf.PdfDocument.FromFile(pdf_file)

        # Extract all pages to a folder as image files
        folder_path = "images"
        pdf.RasterizeToImageFiles(os.path.join(folder_path, "*.png"))

        # Get the list of image files in the folder
        image_paths = []
        for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0])):
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                image_paths.append(os.path.join(folder_path, filename))
        return image_paths
    
    def get_last_rectangle(self):
        if self.user_keylogger.rectangles_selected:
            rect = self.user_keylogger.rectangles_selected[-1]
            image = ImageGrab.grab(bbox = [rect[0][0], rect[0][1], rect[1][0]-rect[0][0], rect[1][1] - rect[0][1]])
            image.save("last_rect_img.jpg")
            # This is what the image is accessible as for further usage
                    

    def select_pdf(self):
        self.clear_image_folder()
        self.current_pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.current_pdf_path:
            self.convert_and_display_images()

    def convert_and_display_images(self):
        self.image_paths = self.convert_pdf_to_images(self.current_pdf_path)

        if self.image_paths:
            self.current_page = 0
            self.show_current_page()

    def show_current_page(self):
        print(self.image_paths)
        if self.image_paths:
            self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_page < len(self.image_paths) - 1 else tk.DISABLED)
            # Fairly explanatory, but just checks that there is a previous and next page to access or else it's disabled
            self.goto_button.config(state=tk.NORMAL)

            for widget in self.image_frame.winfo_children():
                widget.destroy()

            img_path = self.image_paths[self.current_page]
            image = Image.open(img_path)

            # The image wouldn't fit in the bounds so i resized it
            max_width = self.root.winfo_screenwidth() * 0.75
            max_height = self.root.winfo_screenheight() * 0.75
            image.thumbnail((max_width, max_height))
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.image_frame, image=photo)
            label.image = photo
            label.pack(pady=5)

    def turn_page_back(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()

    def turn_page_forward(self):
        if self.current_page < len(self.image_paths) - 1:
            self.current_page += 1
            self.show_current_page()

    def turn_to_specific_page(self):
        target_page = simpledialog.askinteger("Which page do you want to turn to?", f"Enter the page number, "
                                                f"from 1 to {len(self.image_paths)}: ", parent=self.root)
        if target_page is not None and 1 <= target_page <= len(self.image_paths):
            self.current_page = target_page - 1
            self.show_current_page()

        else:
            tk.messagebox.showwarning("Invalid Page", f"Page number should be between 1 and {len(self.image_paths)}")


    def clear_image_folder(self):
        # This clears all of the images from the current Images folder, which prevents reading into previous gen pdf slides
        directory_path = "images"#os.getcwd()
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except OSError as e:
                print(f"Path {file_path} is inaccessible", e)

if __name__ == "__main__":
    root = tk.Tk()
    app = front_end(root)
    root.mainloop()
