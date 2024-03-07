import keyboard
import subprocess
import time
import os

from pynput import keyboard
from pynput import mouse


# noinspection PyMethodMayBeStatic
# -- This is because it was annoying me
class systemInteractions:
    def __init__(self):
        self.__brew_dependencies = []
        self.dependencies_installed = self.install_dependencies(self.__brew_dependencies)

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
        self.__path = settings_file_path
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

    def select_rectangle(self):
        self.reset()
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()
        return self.return_last_rectangle()


userInt = user_interaction(None)
userInt.keyTrackers()

while True:
    print("Main loop is going on")
    time.sleep(5)
