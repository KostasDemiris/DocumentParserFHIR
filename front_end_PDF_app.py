import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import os
import ironpdf

class front_end:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reading Application")

        self.current_pdf_path = None
        self.image_paths = []
        self.current_page = 0

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="PDF Reading Application", font=("Georgia", 16))
        self.label.pack(pady=10)

        self.select_button = tk.Button(self.root, text="Select PDF", command=self.select_pdf)
        self.select_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.prev_button = tk.Button(self.root, text="Previous Page", command=self.show_previous_page,
                                     state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)
        # Can't be selected until the pdf has been selected

        self.next_button = tk.Button(self.root, text="Next Page", command=self.show_next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.goto_button = tk.Button(self.root, text="Go to Page", command=self.goto_page, state=tk.DISABLED)
        self.goto_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(side=tk.LEFT, padx=5, pady=5)

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

    def select_pdf(self):
        self.clear_image_folder()
        self.current_pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.current_pdf_path:
            self.display_pdf()

    def convert_and_display_images(self):
        self.image_paths = self.convert_pdf_to_images(self.pdf_path)

        if self.image_paths:
            self.current_page = 0
            self.show_current_page()

    def show_current_page(self):
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
                                                f"from 1 to {len(self.image_paths) - 1}: ", parent=self.root)
        if target_page is not None and 1 <= target_page < len(self.image_paths):
            self.current_page = target_page - 1
            self.show_current_page()

        else:
            tk.messagebox.showwarning("Invalid Page", f"Page number should be between 1 and {len(self.image_paths)-1}")


    def clear_image_folder(self):
        # This clears all of the images from the current directory, which prevents reading into previous gen pdf slides
        directory_path = os.getcwd()
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

