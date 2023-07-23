import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import psutil
import platform
import csv
import pandas as pd

class PCPartOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PartGear: Beta")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        min_width = 1280
        min_height = 720
        
        self.parts = []  # List to store the PC parts
        self.part_types = ["CPU", "GPU", "RAM", "Storage", "Motherboard", "PSU", "Case", "Cooler", "Other"]
        
        # Add a dictionary to store stock quantity for each part
        self.stock = {}
        
        # Create a frame for the buttons
        self.buttons_frame = tk.Frame(root)
        self.buttons_frame.pack(pady=10)
        
        self.label_part_name = tk.Label(self.buttons_frame, text="Enter PC Part:")
        self.label_part_name.pack(side=tk.LEFT, padx=5)
        
        self.part_name_entry = tk.Entry(self.buttons_frame)
        self.part_name_entry.pack(side=tk.LEFT, padx=5)
        
        self.label_part_type = tk.Label(self.buttons_frame, text="Select Part Type:")
        self.label_part_type.pack(side=tk.LEFT, padx=5)
        
        self.part_type_var = tk.StringVar(root)
        self.part_type_var.set(self.part_types[0])  # Set the default part type
        self.part_type_menu = tk.OptionMenu(self.buttons_frame, self.part_type_var, *self.part_types)
        self.part_type_menu.pack(side=tk.LEFT, padx=5)
        
        self.label_stock_quantity = tk.Label(self.buttons_frame, text="Stock Quantity:")
        self.label_stock_quantity.pack(side=tk.LEFT, padx=5)
        
        self.stock_quantity_entry = tk.Entry(self.buttons_frame)
        self.stock_quantity_entry.pack(side=tk.LEFT, padx=5)
        
        self.add_button = tk.Button(self.buttons_frame, text="Add Part", command=self.add_part)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.edit_button = tk.Button(self.buttons_frame, text="Edit Part", command=self.edit_part)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = tk.Button(self.buttons_frame, text="Delete Part", command=self.delete_part)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = tk.Button(self.buttons_frame, text="Save to File", command=self.save_to_file)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.load_button = tk.Button(self.buttons_frame, text="Load from File", command=self.load_from_file)
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        self.search_button = tk.Button(self.buttons_frame, text="Search Parts", command=self.search_parts)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(self.buttons_frame, text="Clear All Parts", command=self.clear_all_parts)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        
        self.sort_button = tk.Button(self.buttons_frame, text="Sort Parts", command=self.sort_parts)
        self.sort_button.pack(side=tk.LEFT, padx=5)
        
        self.export_csv_button = tk.Button(self.buttons_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_csv_button.pack(side=tk.LEFT, padx=5)
        
        self.export_excel_button = tk.Button(self.buttons_frame, text="Export to Excel", command=self.export_to_excel)
        self.export_excel_button.pack(side=tk.LEFT, padx=5)
        
        self.part_details_button = tk.Button(self.buttons_frame, text="Part Details", command=self.part_details)
        self.part_details_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the parts listbox
        self.listbox_frame = tk.Frame(root)
        self.listbox_frame.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)
        
        self.total_parts_label = tk.Label(self.listbox_frame, text="Total Parts: 0")
        self.total_parts_label.pack(pady=5)
        
        self.view_parts_listbox = tk.Listbox(self.listbox_frame, selectmode=tk.SINGLE)
        self.view_parts_listbox.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self.listbox_frame, command=self.view_parts_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.view_parts_listbox.config(yscrollcommand=self.scrollbar.set)
    
    def add_part(self):
        part_name = self.part_name_entry.get()
        part_type = self.part_type_var.get()
        stock_quantity = self.stock_quantity_entry.get()
        
        if not part_name:
            messagebox.showwarning("Error", "Please enter a part name.")
            return
        
        try:
            stock_quantity = int(stock_quantity)
            if stock_quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Please enter a valid non-negative stock quantity.")
            return
        
        self.parts.append((part_name, part_type))
        self.stock[part_name] = stock_quantity
        self.update_listbox()
        messagebox.showinfo("Success", f"{part_name} ({part_type}) has been added with stock quantity {stock_quantity}.")
        self.part_name_entry.delete(0, tk.END)
        self.stock_quantity_entry.delete(0, tk.END)
        
    def edit_part(self):
        selected_part = self.get_selected_part()
        if selected_part:
            index, part_info = selected_part
            part_name, part_type = part_info
            stock_quantity = self.stock[part_name]
            self.part_name_entry.delete(0, tk.END)
            self.part_name_entry.insert(0, part_name)
            self.part_type_var.set(part_type)
            self.stock_quantity_entry.delete(0, tk.END)
            self.stock_quantity_entry.insert(0, stock_quantity)
            self.add_button.config(command=lambda: self.update_part(index))
            self.edit_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            
    def update_part(self, index):
        new_part_name = self.part_name_entry.get()
        new_part_type = self.part_type_var.get()
        new_stock_quantity = self.stock_quantity_entry.get()
        
        if not new_part_name:
            messagebox.showwarning("Error", "Please enter a new part name.")
            return
        
        try:
            new_stock_quantity = int(new_stock_quantity)
            if new_stock_quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Please enter a valid non-negative stock quantity.")
            return
        
        old_part_name, _ = self.parts[index]
        self.parts[index] = (new_part_name, new_part_type)
        self.stock[new_part_name] = new_stock_quantity
        del self.stock[old_part_name]
        self.update_listbox()
        messagebox.showinfo("Success", f"{old_part_name} has been updated to {new_part_name} ({new_part_type}) with stock quantity {new_stock_quantity}.")
        self.part_name_entry.delete(0, tk.END)
        self.stock_quantity_entry.delete(0, tk.END)
        self.add_button.config(command=self.add_part)
        self.edit_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        
    def delete_part(self):
        selected_part = self.get_selected_part()
        if selected_part:
            index, part_info = selected_part
            part_name, _ = part_info
            del self.stock[part_name]
            self.parts.pop(index)
            self.update_listbox()
            messagebox.showinfo("Success", f"{part_name} has been deleted.")
        else:
            messagebox.showwarning("Error", "Please select a part to delete.")
            
    def part_details(self):
        selected_part = self.get_selected_part()
        if selected_part:
            _, part_info = selected_part
            part_name, part_type = part_info
            stock_quantity = self.stock[part_name]
            details = f"Part Type: {part_type}\nPart Name: {part_name}\nStock Quantity: {stock_quantity}"
            messagebox.showinfo("Part Details", details)
        else:
            messagebox.showwarning("Error", "Please select a part to view details.")
            
    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                for part_name, part_type in self.parts:
                    stock_quantity = self.stock.get(part_name, 0)
                    file.write(f"{part_name},{part_type},{stock_quantity}\n")
            messagebox.showinfo("Success", "Parts have been saved to the file.")
            
    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.parts.clear()
            self.stock.clear()
            with open(file_path, "r") as file:
                for line in file:
                    # Check if the line contains at least three values separated by commas
                    if "," in line:
                        part_name, part_type, stock_quantity = line.strip().split(",", 2)
                        try:
                            stock_quantity = int(stock_quantity)
                            if stock_quantity < 0:
                                raise ValueError
                        except ValueError:
                            # Handle improperly formatted stock quantity
                            print(f"Warning: Skipping line with improper stock quantity format: {line}")
                            continue
                        self.parts.append((part_name, part_type))
                        self.stock[part_name] = stock_quantity
                    else:
                        # Handle improperly formatted lines
                        print(f"Warning: Skipping line with improper format: {line}")
            self.update_listbox()
            messagebox.showinfo("Success", "Parts have been loaded from the file.")
            
    def update_listbox(self):
        self.view_parts_listbox.delete(0, tk.END)
        for part_name, part_type in self.parts:
            stock_quantity = self.stock.get(part_name, 0)
            self.view_parts_listbox.insert(tk.END, f"{part_name} ({part_type}) - Stock: {stock_quantity}")
        self.total_parts_label.config(text=f"Total Parts: {len(self.parts)}")
        
    def get_selected_part(self):
        selected_index = self.view_parts_listbox.curselection()
        if selected_index:
            index = int(selected_index[0])
            part_info = self.parts[index]
            return index, part_info
        else:
            return None
            
    def search_parts(self):
        query = self.part_name_entry.get()
        if not query:
            messagebox.showwarning("Error", "Please enter a part name to search.")
            return

        results = [part for part in self.parts if query.lower() in part[0].lower()]
        if results:
            messagebox.showinfo("Search Results", f"Matching parts:\n{', '.join([f'{part[0]} ({part[1]})' for part in results])}")
        else:
            messagebox.showinfo("Search Results", "No matching parts found.")
            
    def clear_all_parts(self):
        self.parts.clear()
        self.stock.clear()
        self.update_listbox()
        messagebox.showinfo("Success", "All parts have been cleared.")
        
    def detect_specs(self):
        cpu_info = platform.processor()
        gpu_info = f"GPU: {', '.join(psutil.gpu_devices())}" if psutil.gpu_devices() else "GPU: Not Found"
        ram_info = f"RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB"
        system_info = f"System: {platform.system()} {platform.release()}"
        messagebox.showinfo("PC Specs", f"{cpu_info}\n{gpu_info}\n{ram_info}\n{system_info}")
        
    def sort_parts(self):
        self.parts.sort(key=lambda part: (part[1], part[0].lower()))
        self.update_listbox()
        messagebox.showinfo("Success", "Parts have been sorted.")
        
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Part Name", "Part Type", "Stock Quantity"])
                for part_name, part_type in self.parts:
                    stock_quantity = self.stock.get(part_name, 0)
                    csv_writer.writerow([part_name, part_type, stock_quantity])
            messagebox.showinfo("Success", "Parts have been exported to CSV.")
            
    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            data = {"Part Name": [], "Part Type": [], "Stock Quantity": []}
            for part_name, part_type in self.parts:
                stock_quantity = self.stock.get(part_name, 0)
                data["Part Name"].append(part_name)
                data["Part Type"].append(part_type)
                data["Stock Quantity"].append(stock_quantity)
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", "Parts have been exported to Excel.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PCPartOrganizerApp(root)
    root.mainloop()
