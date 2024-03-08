import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
import os
import ironpdf 

def convert_pdf_to_images(pdf_file):
    # For big PDF's, this can lag a lot. Ps got this from some tutorial
    pdf = ironpdf.PdfDocument.FromFile(pdf_file)
    # Extract all pages to a folder as image files
    folder_path = "images"
    pdf.RasterizeToImageFiles(os.path.join(folder_path, "*.png"))
    # List to store the image paths
    image_paths = []
    # Get the list of image files in the folder
    for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0])):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
            image_paths.append(os.path.join(folder_path, filename))
    return image_paths

def clear_image_folder():
    # Clears all other images out of the storage folder so only the most recently viewed one is displayed
    folder_path = "images"
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

class PDFToImageConverterApp:
    # Most of this is done by ChatGPT, just to be honest. I'll do it at some point but i don't like GUI design :(
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Image Converter")

        self.pdf_path = ""
        self.image_paths = []
        self.current_page = 0

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="PDF to Image Converter", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.select_button = tk.Button(self.root, text="Select PDF", command=self.select_pdf)
        self.select_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.prev_button = tk.Button(self.root, text="Previous Page", command=self.show_previous_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.next_button = tk.Button(self.root, text="Next Page", command=self.show_next_page, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.goto_button = tk.Button(self.root, text="Go to Page", command=self.goto_page, state=tk.DISABLED)
        self.goto_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(padx=10, pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)

    def select_pdf(self):
        clear_image_folder()  # Clear existing images before selecting new PDF
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.pdf_path:
            self.convert_and_display_images()

    def convert_and_display_images(self):
        # Convert PDF to images
        self.image_paths = convert_pdf_to_images(self.pdf_path)

        if self.image_paths:
            self.current_page = 0
            self.show_current_page()

    def show_current_page(self):
        if self.image_paths:
            self.prev_button.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_page < len(self.image_paths) - 1 else tk.DISABLED)
            self.goto_button.config(state=tk.NORMAL)

            # Clear previous images if any
            for widget in self.image_frame.winfo_children():
                widget.destroy()

            img_path = self.image_paths[self.current_page]
            image = Image.open(img_path)
            # Resize the image to fit within the screen dimensions
            max_width = self.root.winfo_screenwidth() * 0.8
            max_height = self.root.winfo_screenheight() * 0.8
            image.thumbnail((max_width, max_height))
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.image_frame, image=photo)
            label.image = photo
            label.pack(pady=5)

    def show_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()

    def show_next_page(self):
        if self.current_page < len(self.image_paths) - 1:
            self.current_page += 1
            self.show_current_page()

    def goto_page(self):
        max_page = len(self.image_paths)
        page = simpledialog.askinteger("Go to Page", f"Enter page number (1 - {max_page}):", parent=self.root)
        if page is not None:
            if 1 <= page <= max_page:
                self.current_page = page - 1
                self.show_current_page()
            else:
                tk.messagebox.showwarning("Invalid Page", f"Page number should be between 1 and {max_page}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToImageConverterApp(root)
    root.mainloop()
