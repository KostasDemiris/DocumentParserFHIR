import pynput.mouse
from pynput.mouse import Listener


class mouseTracker:
    def _init_(self):
        self.down = [0, 0]
        self.up = [0, 0]
        self.selected_rectangle = None

    def begin_tracking(self):
        self.reset()
        # Nothing should happen even if this isn't called, but just in case they manually try to query selected rect
        # without any clicks
        with Listener(on_click=self.left_down) as listener:
            listener.join()  # This is now listening into any mouse clicks

    def reset(self):
        self.down = [0, 0]
        self.up = [0, 0]
        self.selected_rectangle = None

    def left_down(self, x, y, button, pressed):
        # see what argument is passed.
        if pressed and button.name == "left":
            # Do something when the mouse key is pressed.
            print('The "{}" mouse key has held down'.format(button.name))
            print(f"The current mouse position is {x, y}\n")
            self.down = [x, y]

        elif button.name == "left":  # it's been released
            # Do something when the mouse key is released.
            print('The "{}" mouse key is released'.format(button.name))
            print(f"The current mouse position is {x, y}\n")
            self.up = [x, y]
            self.selected_rectangle = [[(min(self.down[0], self.up[0]), min(self.down[1], self.up[1]))],
                                       [(max(self.down[0], self.up[0]), max(self.down[1], self.up[1]))]]
            print(f"{self.selected_rectangle} is the selected rectangle")
            return False  # This kills the thread that the listener works on.

            # This means they have click the button every time they want to select a pdf section, which makes it more
            # annoying but less likely to incorrectly identify any particular section.

    def get_last_selected(self):
        return self.selected_rectangle


tracker = mouseTracker()
tracker.begin_tracking()  # This will be called when the relevant button is clicked in the integrated version
