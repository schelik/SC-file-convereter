import os
from PIL import Image
import img2pdf
import tkinter as tk
from tkinter import ttk, filedialog
from fpdf import FPDF
from pathlib import Path
import subprocess
import platform
import sys


class FileDropApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("650x400")
        self.root.title("SC File Converter")
        # load image file
        logo_path = os.path.join(sys._MEIPASS, "logo.png")
        logo_image = tk.PhotoImage(file=logo_path)

        # set logo as window icon
        self.root.iconphoto(True, logo_image)

        # create grid to display dropped files
        self.tree = ttk.Treeview(
            self.root, columns=("name", "type", "path"), show="headings"
        )
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("path", text="Path")
        self.tree.column("name", width=200, anchor="center")
        self.tree.column("type", width=150, anchor="center")
        self.tree.column("path", width=400, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # allow the grid to accept file drops
        self.tree.bind("<Button-1>", lambda event: self.tree.selection_clear())
        self.tree.bind("<Button-1>", self.select_item, True)
        self.tree.bind("<B1-Motion>", self.drag_n_drop)
        self.tree.bind("<ButtonRelease-1>", self.drop_files)
        self.tree.bind(
            "<Enter>", lambda event: self.tree.config(style="hover.Treeview")
        )
        self.tree.bind("<Leave>", lambda event: self.tree.config(style="Treeview"))
        self.tree.config(selectmode="extended", style="Treeview")

        # add a scrollbar to the grid
        self.scrollbar = ttk.Scrollbar(self.tree)
        self.scrollbar.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # create a frame to center the dropdown and button
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, pady=10)

        # create an upload button to select files to upload
        self.upload_button = ttk.Button(
            self.frame, text="Upload", command=self.open_file_dialog
        )
        self.upload_button.pack(side=tk.LEFT, padx=10, pady=10)

        # create a dropdown menu to select output file type
        self.output_type = tk.StringVar()
        self.output_type.set("PDF")
        self.output_menu = ttk.OptionMenu(self.frame, self.output_type, "PDF", "PDF")
        self.output_menu.pack(side=tk.LEFT, padx=10)

        # create a button to convert files to selected output type
        self.convert_button = ttk.Button(
            self.frame, text="Convert", command=self.convert_files, state=tk.DISABLED
        )
        self.convert_button.pack(side=tk.LEFT, padx=10)

        # create a context menu to delete rows and open file location
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(
            label="Open File Location", command=self.open_file_location
        )
        self.context_menu.add_command(label="Delete", command=self.delete_row)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.root.mainloop()

    def open_file_dialog(self):
        # open file dialog to select file
        file_path = filedialog.askopenfilenames()
        # add file paths to treeview
        for path in file_path:
            name = path.split("/")[-1]
            file_type = self.get_file_type(path)
            self.tree.insert("", tk.END, values=(name, file_type, path))

    def drag_n_drop(self, event):
        self.tree.config(style="dragdrop.Treeview")

    def drop_files(self, event):
        self.tree.config(style="Treeview")

    def get_file_type(self, path):
        # return file type based on extension
        extension = path.split(".")[-1]
        if extension == "pdf":
            return "PDF"
        else:
            return extension.upper()

    def select_item(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            if item in self.tree.selection():
                self.tree.selection_remove(item)
            else:
                self.tree.selection_add(item)
        # enable/disable the "Convert" button based on whether any items are selected
        selected_items = self.tree.selection()
        if selected_items:
            self.convert_button.config(state=tk.NORMAL)
        else:
            self.convert_button.config(state=tk.DISABLED)

    def convert_files(self):
        # disable the "Convert" button
        self.convert_button.config(state=tk.DISABLED)

        # get selected files and convert to selected output type
        selected_items = self.tree.selection()
        if not selected_items:
            return

        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if output_dir:
            for item in selected_items:
                path = self.tree.item(item, "values")[2]
                output_name = os.path.splitext(os.path.basename(path))[0] + ".pdf"
                output_path = os.path.join(output_dir, output_name)
                self.convert_to_output_type(item, path, output_path)
        else:
            for item in selected_items:
                path = self.tree.item(item, "values")[2]
                output_name = os.path.splitext(os.path.basename(path))[0] + ".pdf"
                output_dir = os.path.dirname(path)
                output_path = os.path.join(output_dir, output_name)
                self.convert_to_output_type(item, path, output_path)

        # enable the "Convert" button and update treeview
        for item in selected_items:
            name = self.tree.item(item, "values")[0]
            file_type = self.get_file_type(self.tree.item(item, "values")[2])
            self.tree.item(
                item, values=(name, file_type, self.tree.item(item, "values")[2])
            )
        self.convert_button.config(state=tk.NORMAL)

    def convert_to_output_type(self, item, path, output_path):
        # convert file to selected output type and update treeview
        if path.endswith(".pdf"):
            # file is already a PDF, so no conversion needed
            self.tree.item(
                item, values=(self.tree.item(item, "values")[0], "PDF", path)
            )
            return

        if path.endswith(".txt"):
            # convert text file to PDF
            with open(path, "r") as f:
                text = f.read()

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 5, text)
            pdf.output(output_path)

        elif path.endswith((".jpg", ".jpeg", ".png", ".bmp")):
            # convert image file to PDF
            with Image.open(path) as img:
                img = img.convert("RGB")
                with open(output_path, "wb") as f:
                    f.write(img2pdf.convert(img.filename))

        # update the path in the treeview with the output path
        name = os.path.splitext(os.path.basename(path))[0] + ".pdf"
        file_type = self.get_file_type(output_path)
        self.tree.item(item, values=(name, file_type, output_path))

    def delete_row(self):
        # delete selected rows from treeview
        selected_items = self.tree.selection()
        for item in selected_items:
            self.tree.delete(item)

    def show_context_menu(self, event):
        # show context menu at the selected row
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)

    def open_file_location(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        for item in selected_items:
            path = Path(self.tree.item(item, "values")[2]).resolve()
            parent_dir = path.parent
            # open the file explorer or finder to the parent directory containing the file
            # get the operating system name
            operating_system = platform.system()

            # open the file explorer or finder to the parent directory containing the file
            if operating_system == "Darwin":
                subprocess.run(["open", parent_dir], check=True)  # for macOS
            elif operating_system == "Windows":
                subprocess.run(
                    ["explorer", "/select,", str(path)], check=True
                )  # for Windows
            elif operating_system == "Linux":
                subprocess.run(["nautilus", parent_dir], check=True)  # for Linux
            else:
                print("Unsupported operating system.")


if __name__ == "__main__":
    app = FileDropApp()
