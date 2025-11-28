import tkinter as tk
from tkinter import messagebox
import sqlite3
import datetime
from tkinter import ttk

# --- 1. Database and Logic Functions (Reused from main.py) ---

DATABASE_NAME = "bmi_records.db"

def initialize_database():
    """Connects and creates the measurements table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_time TEXT NOT NULL,
            weight_kg REAL NOT NULL,
            height_m REAL NOT NULL,
            bmi_value REAL NOT NULL,
            bmi_category TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def calculate_bmi(weight_kg, height_m):
    """Calculates BMI and determines the category."""
    if height_m <= 0 or weight_kg <= 0:
        raise ValueError("Weight and height must be positive values.")
        
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obesity"
        
    return bmi, category

def save_record(weight_kg, height_m, bmi_value, bmi_category):
    """Saves the new measurement record to the database."""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO measurements (date_time, weight_kg, height_m, bmi_value, bmi_category) 
           VALUES (?, ?, ?, ?, ?)""", 
        (current_time, weight_kg, height_m, bmi_value, bmi_category)
    )
    conn.commit()
    conn.close()
def fetch_records():
    """ดึงข้อมูลประวัติการวัดทั้งหมด"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    # Note: Fetch column names along with data for better table headers
    cursor.execute("SELECT * FROM measurements ORDER BY date_time DESC")
    records = cursor.fetchall()
    conn.close()
    return records
    
# --- 2. GUI Application Class ---

class BMICalculatorApp:
    def __init__(self, master):
        self.master = master
        master.title("BMI Tracker")
        master.geometry("400x450") # Set initial window size

        initialize_database()

        # --- Variables to store user input and results ---
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.bmi_result_var = tk.StringVar(value="Enter values and click Calculate")
        self.category_var = tk.StringVar(value="")

        # --- Create Widgets ---
        self.create_widgets()

    def create_widgets(self):
        # Frame for input fields
        input_frame = tk.Frame(self.master, padx=10, pady=10)
        input_frame.pack(pady=10)

        # Weight Input
        tk.Label(input_frame, text="Weight (kg):").grid(row=0, column=0, sticky='w', pady=5)
        self.weight_entry = tk.Entry(input_frame, textvariable=self.weight_var)
        self.weight_entry.grid(row=0, column=1, padx=10)

        # Height Input
        tk.Label(input_frame, text="Height (cm):").grid(row=1, column=0, sticky='w', pady=5)
        self.height_entry = tk.Entry(input_frame, textvariable=self.height_var)
        self.height_entry.grid(row=1, column=1, padx=10)
        
        # Calculate Button
        self.calc_button = tk.Button(self.master, text="Calculate BMI", command=self.calculate_and_display, 
                                     bg='green', fg='white', width=20)
        self.calc_button.pack(pady=10)

        # --- Results Display ---
        
        # BMI Label
        tk.Label(self.master, text="Your BMI:", font=('Helvetica', 12, 'bold')).pack(pady=5)
        self.result_label = tk.Label(self.master, textvariable=self.bmi_result_var, 
                                     font=('Helvetica', 16, 'bold'), fg='blue')
        self.result_label.pack()
        
        # Category Label
        self.category_label = tk.Label(self.master, textvariable=self.category_var, 
                                       font=('Helvetica', 12, 'italic'))
        self.category_label.pack(pady=5)
        
        # Save Button
        self.save_button = tk.Button(self.master, text="Save Record", command=self.save_current_record, 
                                     width=20, state=tk.DISABLED) # Start disabled
        self.save_button.pack(pady=10)
        
        # View History Button
        self.history_button = tk.Button(self.master, text="View History (Table)", command=self.show_history_window, width=20)
        self.history_button.pack(pady=5)
        
        # Store last successful calculation for saving
        self.last_bmi_data = None 

    def calculate_and_display(self):
        """Fetches input, validates, calculates BMI, and updates display."""
        try:
            # 1. Input Validation and Conversion
            weight_kg = float(self.weight_var.get())
            height_cm = float(self.height_var.get())
            height_m = height_cm / 100 # Convert cm to meters

            # 2. Business Logic
            bmi_value, bmi_category = calculate_bmi(weight_kg, height_m)
            
            # 3. Update Display
            self.bmi_result_var.set(f"{bmi_value:.2f}")
            self.category_var.set(f"Category: {bmi_category}")
            self.save_button.config(state=tk.NORMAL) # Enable save button on success
            
            # Store data for potential saving
            self.last_bmi_data = (weight_kg, height_m, bmi_value, bmi_category)

        except ValueError as e:
            # Handle non-numeric or non-positive errors
            messagebox.showerror("Input Error", "Please enter valid, positive numbers for weight and height.")
            self.bmi_result_var.set("Error")
            self.category_var.set("")
            self.save_button.config(state=tk.DISABLED)

    def save_current_record(self):
        """Saves the last calculated BMI record."""
        if self.last_bmi_data:
            save_record(*self.last_bmi_data)
            messagebox.showinfo("Success", "BMI Record saved to history!")
            self.save_button.config(state=tk.DISABLED) # Disable button after saving
            self.last_bmi_data = None
        else:
            messagebox.showwarning("Warning", "Calculate BMI before saving.")
   

    def show_history_window(self):
        """Opens a new window to display history records in a table."""
        # This function should fetch records from DB and display them in a new Tkinter window/table widget
        # For simplicity in this example, we just display a message
        messagebox.showinfo("History Viewer", "Viewing history is implemented here (requires a separate table widget).")
        
        # You would implement the actual data fetching and display here:
        # records = self.fetch_records()
        # display_table_in_new_window(records)
    def show_history_window(self):
        """Opens a new window to display history records in a table (Treeview)."""
        records = fetch_records()
        
        if not records:
            messagebox.showinfo("History", "No records found in the database.")
            return
            
        history_window = tk.Toplevel(self.master)
        history_window.title("BMI History Records")
        
        # --- Define Columns and Headers ---
        columns = ("ID", "Date/Time", "Weight (kg)", "Height (m)", "BMI", "Category")
        
        # Create Treeview widget
        self.tree = ttk.Treeview(history_window, columns=columns, show="headings")
        
        # Configure column widths and headers
        column_widths = [50, 160, 90, 90, 60, 140]
        
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')
        
        # --- Insert Data into the Treeview ---
        for record in records:
            # Format the BMI and Weight/Height for cleaner display
            # record = (record_id, date_time, weight_kg, height_m, bmi_value, bmi_category)
            
            display_record = (
                record[0],
                record[1],
                f"{record[2]:.2f}", # Weight
                f"{record[3]:.2f}", # Height
                f"{record[4]:.2f}", # BMI Value
                record[5]          # Category
            )
            self.tree.insert("", tk.END, values=display_record)
            
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the widgets
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
# --- 3. Main Execution ---

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()