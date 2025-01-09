import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from PIL import Image, ImageTk
import time
import cv2
customer_path = "C:\\Users\\matan\\OneDrive\\Desktop\\Customers data.csv"
clothe_path = "C:\\Users\\matan\\OneDrive\\Desktop\\Clothes data.csv"

class SignInWindow:
    def _init_(self, master):
        self.master = master
        self.master.title("Sign-In")
        self.master.geometry("300x150")
        self.master.configure(bg="#B0C4DE")

        self.id_label = tk.Label(self.master, text="Enter Customer ID (9 digits):", font=("Arial", 12), bg="#F0F0F0")
        self.id_label.pack(pady=5)

        self.id_var = tk.StringVar()
        self.id_entry = tk.Entry(self.master, font=("Arial", 12), textvariable=self.id_var, validate="key")
        self.id_entry.pack(pady=5)

        # Set validation function for customer ID entry field
        self.id_entry.config(validatecommand=(self.id_entry.register(self.validate_customer_id), "%P"))

        self.submit_button = tk.Button(self.master, text="Submit", font=("Arial", 12), command=self.open_bought_window)
        self.submit_button.pack(pady=10)

    def validate_customer_id(self, input_text):
        # Validation function for customer ID entry field
        if input_text.isdigit() and len(input_text) == 9:
            return True
        return False

    def open_bought_window(self):
        customer_id = self.id_entry.get()
        customer_id = int(customer_id)

        # Load the customer data from the CSV file
        try:
            customer_data = pd.read_csv(customer_path)

        except FileNotFoundError:
            messagebox.showerror("Error", "Customer data file not found.")
            return

        # Check if the customer ID exists in the data
        if customer_id in customer_data["ID"].values:
            customer_name = customer_data.loc[customer_data["ID"] == customer_id, "ContactFirstName"].values[0]
            messagebox.showinfo("Success", f"Welcome, {customer_name}!")
            self.master.withdraw()  # Hide the current screen
            new_screen = tk.Toplevel(self.master)
            bought_window = BoughtWindow(new_screen, customer_id, customer_name)

        else:
            messagebox.showinfo("Error", "Customer does not exist.")

        # Clear the entry field after processing
        self.id_var.set("")



class BoughtWindow:
    def _init_(self, master, customer_id, customer_name):
        self.master = master
        self.master.title("Bought Items")
        self.master.geometry("500x150")
        self.customer_name = customer_name

        # Load the customer data from the CSV file
        try:
            customer_data = pd.read_csv(customer_path)

        except FileNotFoundError:
            messagebox.showerror("Error", "Customer data file not found.")
            self.master.destroy()
            return

        # Retrieve the "Bought" column for the given customer ID
        self.bought_items = customer_data.loc[customer_data["ID"] == customer_id, "Bought"].values[0]

        bought_label = tk.Label(self.master, text=f"Bought Items: {self.bought_items}", font=("Arial", 12))
        bought_label.pack(pady=20)

        back_button = tk.Button(self.master, text="Continue", font=("Arial", 12), command=self.open_newest_entries_window)
        back_button.pack(pady=10)

        self.master.pack_slaves()

    def open_newest_entries_window(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        registration_scene = ClothesMenu(new_screen, self.customer_name, self.bought_items)



class ClothesMenu:
    def _init_(self, master, customer_name, bought_items):
        self.master = master
        self.master.title("Clothes Menu")
        self.master.geometry("400x500")
        self.count = 0
        self.details_window = None


        try:
            clothes_data = pd.read_csv(clothe_path, encoding="ISO-8859-1")
            customers_data = pd.read_csv(customer_path)
            self.customers_data = customers_data

            self.clothes_data = clothes_data
            self.product_names = clothes_data["Product Name"].tolist()
            if ',' in bought_items:
                the_list = bought_items.split(',')
                self.product_names = [item for item in self.product_names if item not in the_list]

            else:
                self.product_names.remove(bought_items)
                self.customers_data = customers_data
                self.count = customers_data[customers_data["ContactFirstName"] == customer_name].index[0]
        except FileNotFoundError:
            messagebox.showerror("Error", "Clothes data file not found.")
            return

        self.create_menu()

    def create_menu(self):
        self.pressed_lst = [prod for prod in self.product_names if int(self.customers_data[prod][self.count]) >= 2]

        self.product_listbox = tk.Listbox(self.master, selectmode=tk.SINGLE, font=("Arial", 12))
        for product_name in self.pressed_lst:
            self.product_listbox.insert(tk.END, product_name)
        self.product_listbox.pack(pady=10)

        view_details_button = tk.Button(self.master, text="View Details", font=("Arial", 12), command=self.view_details)
        view_details_button.pack(pady=5)

        menu_return = tk.Button(self.master, text="Back to menu", font=("Arial", 12), command=self.back_to_menu)
        menu_return.pack(pady=5)

    def view_details(self):
        selected_product_index = self.product_listbox.curselection()
        if not selected_product_index:
            messagebox.showwarning("Warning", "Please select a product to view details.")
            return

        selected_product_index = selected_product_index[0]
        selected_product_name = self.product_names[selected_product_index]
        selected_product_data = self.clothes_data[self.clothes_data["Product Name"] == selected_product_name]

        if self.details_window and self.details_window.winfo_exists():
            self.details_window.destroy()

        self.details_window = tk.Toplevel(self.master)
        self.details_window.title("Product Details")
        self.details_window.geometry("400x300")

        self.start_time = time.time()
        details_label = tk.Label(self.details_window, text=f"Details for: {selected_product_name}",
                                 font=("Arial", 12, "bold"))
        details_label.pack(pady=10)

        for index, row in selected_product_data.iterrows():
            entry_label = tk.Label(self.details_window, text="========== Entry ==========", font=("Arial", 12, "bold"))
            entry_label.pack()

            type_label = tk.Label(self.details_window, text=f"Type: {row['Type']}", font=("Arial", 12))
            type_label.pack()
            barcode_label = tk.Label(self.details_window, text=f"Barcode: {row['Barcode']}", font=("Arial", 12))
            barcode_label.pack()
            product_label = tk.Label(self.details_window, text=f"Product: {row['Product Name']}", font=("Arial", 12))
            product_label.pack()
            color_label = tk.Label(self.details_window, text=f"Color: {row['Color']}", font=("Arial", 12))
            color_label.pack()
            price_label = tk.Label(self.details_window, text=f"Price: {row['Price']}", font=("Arial", 12))
            price_label.pack()

        back_button = tk.Button(self.details_window, text="Go Back", font=("Arial", 12), command=self.save_and_go_back)
        back_button.pack(pady=10)

    def save_and_go_back(self):
        self.details_window.withdraw()
        end_time = time.time()
        time_taken = end_time - self.start_time
        selected_product_index = self.product_listbox.curselection()
        selected_product_name = self.pressed_lst[selected_product_index[0]]

        column_name = f"{selected_product_name} Timer"
        column_name_itself = f"{selected_product_name}"

        # Create a copy of the DataFrame slice to avoid SettingWithCopyWarning
        customers_data_copy = self.customers_data.copy()

        timer_update = int(customers_data_copy.at[self.count, column_name])
        timer_update += int(time_taken)
        item_pressed_times = int(customers_data_copy.at[self.count, column_name_itself])
        item_pressed_times += 1

        # Update the copy with the modified values
        customers_data_copy.at[self.count, column_name] = timer_update
        customers_data_copy.at[self.count, column_name_itself] = item_pressed_times

        # Update the original DataFrame with the modified values
        self.customers_data.update(customers_data_copy)

        self.customers_data.to_csv(customer_path, index=False)
        self.master.focus()
        self.master.lift()
        messagebox.showinfo("Info", f"Time taken for {selected_product_name}: {int(time_taken)} seconds")


    def back_to_menu(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        main_scene = OpenWindow(new_screen)

class NewestEntriesWindow:
    def _init_(self, master):
        self.master = master
        self.master.title("Newest Entries")
        self.master.geometry("700x800")

        try:
            clothes_data = pd.read_csv(customer_path, encoding="ISO-8859-1")
            self.clothes_data = clothes_data
        except FileNotFoundError:
            messagebox.showerror("Error", "Clothes data file not found.")
            return

            # Sort the data based on "Date of entry" column in descending order
        clothes_data["Date of entry"] = pd.to_datetime(clothes_data["Date of entry"], format="%d.%m.%y")
        clothes_data.sort_values(by="Date of entry", ascending=False, inplace=True)

        # Get the three newest dates
        newest_dates = clothes_data["Date of entry"].head(3).tolist()

        # Filter rows with the three newest dates
        newest_entries = self.clothes_data[clothes_data["Date of entry"].isin(newest_dates)]


        # Display the details for each row
        k = 1
        for index, row in newest_entries.iterrows():
            entry_label = tk.Label(self.master, text="=========Recommendation " + str(k) + " ==========", font=("Arial", 12, "bold"))
            entry_label.pack()
            k += 1

            type_label = tk.Label(self.master, text=f"Type: {row['Type']}", font=("Arial", 12))
            type_label.pack()
            barcode_label = tk.Label(self.master, text=f"Barcode: {row['Barcode']}", font=("Arial", 12))
            barcode_label.pack()
            product_label = tk.Label(self.master, text=f"Product: {row['Product Name']}", font=("Arial", 12))
            product_label.pack()
            color_label = tk.Label(self.master, text=f"Color: {row['Color']}", font=("Arial", 12))
            color_label.pack()
            price_label = tk.Label(self.master, text=f"Price: {row['Price']}", font=("Arial", 12))
            price_label.pack()
            occasion_label = tk.Label(self.master, text=f"Occasion: {row['Occasion']}", font=("Arial", 12))
            occasion_label.pack()
            date_label = tk.Label(self.master, text=f"Date: {row['Date of entry']}", font=("Arial", 12))
            date_label.pack()

        back_button = tk.Button(self.master, text="Go Back", font=("Arial", 12), command=self.go_back)
        back_button.pack(pady=10)

    def go_back(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        main_scene = OpenWindow(new_screen)


class OpenWindow:
    def _init_(self, master):
        self.master = master
        self.master.title("Virtual Try-On System")
        self.master.geometry("600x400")

        # Add a background image
        bg_image = Image.open("C:\\Users\\matan\\PycharmProjects\\temp\\Clothes.jpg")
        bg_image = bg_image.resize((600, 400))
        self.bg_image = ImageTk.PhotoImage(bg_image)
        self.canvas = tk.Canvas(self.master, width=600, height=400)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.canvas.pack()

        # Add a welcome label
        welcome_label = tk.Label(self.canvas, text="Welcome", font=("Arial", 24, "bold"), fg="blue", bg="white")
        welcome_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        # Add space between buttons
        button_padding = 25

        # Add a button for "Sign up"
        you_button = tk.Button(self.canvas, text="Sign up", font=("Arial", 14), width=15, command=self.open_registration_window,
                               bg="lightblue", fg="black", activebackground="lightblue", activeforeground="black")
        you_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER, y=button_padding)

        # Add a button for "existing clients"
        customer_button = tk.Button(self.canvas, text="Sign in", font=("Arial", 14), width=15,
                                    command=self.open_customer_window,
                                    bg="lightgreen", fg="black", activebackground="lightgreen",
                                    activeforeground="black")
        customer_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER, y=-button_padding)

    def open_registration_window(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        registration_scene = RegistrationWindow(new_screen)


    def sign_in(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        main_scene = OpenWindow(new_screen)


    def open_customer_window(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        sign_in_scene = SignInWindow(new_screen)



### Sign Up window
class RegistrationWindow:
    def _init_(self, master):
        self.master = master
        self.master.title("Registration")
        self.master.geometry("500x600")
        self.master.configure(bg="#B0C4DE")

        self.id_label = tk.Label(self.master, text="ID:", font=("Arial", 12), bg="white")
        self.id_label.pack(pady=10)

        self.id_var = tk.StringVar()
        self.id_entry = tk.Entry(self.master, font=("Arial", 12), textvariable=self.id_var)
        self.id_entry.pack(pady=5)

        # Set validation function for phone number field
        self.id_entry.config(validate="key")
        self.id_entry.config(validatecommand=(self.id_entry.register(self.validate_number), "%P"))

        self.firstName_label = tk.Label(self.master, text="First Name:", font=("Arial", 12), bg="white")
        self.firstName_label.pack(pady=10)

        self.firstName_entry = tk.Entry(self.master, font=("Arial", 12))
        self.firstName_entry.pack(pady=5)

        self.lastName_label = tk.Label(self.master, text="Last Name:", font=("Arial", 12), bg="white")
        self.lastName_label.pack(pady=10)

        self.lastName_entry = tk.Entry(self.master, font=("Arial", 12))
        self.lastName_entry.pack(pady=5)

        self.gender_label = tk.Label(self.master, text="Gender:", font=("Arial", 12), bg="white")
        self.gender_label.pack(pady=10)

        self.gender_options = tk.StringVar()
        self.gender_options.set("M")

        self.gender_frame = tk.Frame(self.master, bg="white")
        self.gender_frame.pack()

        self.male_radio = tk.Radiobutton(self.gender_frame, text="Male", font=("Arial", 12), variable=self.gender_options, value="M", bg="white")
        self.male_radio.pack(side=tk.LEFT, padx=10)

        self.female_radio = tk.Radiobutton(self.gender_frame, text="Female", font=("Arial", 12), variable=self.gender_options, value="F", bg="white")
        self.female_radio.pack(side=tk.LEFT)

        self.phone_label = tk.Label(self.master, text="Phone Number:", font=("Arial", 12), bg="white")
        self.phone_label.pack(pady=10)

        self.phone_var = tk.StringVar()
        self.phone_entry = tk.Entry(self.master, font=("Arial", 12), textvariable=self.phone_var)
        self.phone_entry.pack(pady=5)

        # Set validation function for phone number field
        self.phone_entry.config(validate="key")
        self.phone_entry.config(validatecommand=(self.phone_entry.register(self.validate_number), "%P"))

        self.address_label = tk.Label(self.master, text="Address:", font=("Arial", 12), bg="white")
        self.address_label.pack(pady=10)

        self.address_entry = tk.Entry(self.master, font=("Arial", 12))
        self.address_entry.pack(pady=5)

        self.submit_button = tk.Button(self.master, text="Submit", font=("Arial", 12), command=self.submit_registration)
        self.submit_button.pack(pady=20)

        # Back Button
        self.back_button = tk.Button(self.master, text="Go Back", font=("Arial", 12),  command=self.go_back)
        self.back_button.pack(pady=10)

        # Pack all widgets to display them correctly
        self.master.pack_slaves()

    def validate_number(self, phone_number):
        # Validation function for phone number field
        if phone_number.isdigit() or phone_number == "":
            return True
        else:
            return False

    def submit_registration(self):
        id = self.id_entry.get()
        first_name = self.firstName_entry.get()
        last_name = self.lastName_entry.get()
        gender = self.gender_options.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()

        if id and first_name and last_name and gender and phone and address:

            # List that we want to add as a new row
            lst = [id, first_name, last_name, gender, phone, address]

            self.master.withdraw()  # Hide the current screen
            new_screen = tk.Toplevel(self.master)
            main_scene = PopularityRecomendationScreen(new_screen)

        else:
            tk.messagebox.showerror("Error", "Please fill in all the fields.")


        # You can add code here to store the registration data or perform any other actions

    def go_back(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        main_scene = OpenWindow(new_screen)



class PopularityRecomendationScreen:
    def _init_(self, master):
        self.master = master
        self.master.title("Recomended clothes by popularity")
        self.master.geometry("400x400")
        self.master.configure(bg="#B0C4DE")


        recommend_button = tk.Button(self.master, text="Get Recommendations", font=("Arial", 12),
                                     command=self.get_recommendations)
        recommend_button.pack(pady=10)

    def get_top_words(self, csv_file, column_name, top_n=3):
        from collections import Counter
        words_counter = Counter()
        # Load the CSV file and count word occurrences in the specified column
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                value = row[column_name]
                if value is not None:
                    words = value.split(',')  # Assuming words are separated by commas
                    words_counter.update(words)

        # Retrieve the most common words
        top_words = words_counter.most_common(top_n)
        return top_words

    def get_recommendations(self):
        csv_file_path = customer_path  # Update with your file path
        column_name = 'Bought'
        top_n = 3
        top_words_array = self.get_top_words(csv_file_path, column_name, top_n)

        recommendations_label = tk.Label(self.master,
                                         text=f"Recommended Items that are very popular in our store are: ",

                                         font=("Arial", 12))
        reco_items1_label=tk.Label(self.master,
                                         text=f"{top_words_array[0][0] } and bought {top_words_array[0][1]} times by our customers",
                                         font=("Arial", 12))
        reco_items2_label = tk.Label(self.master,
                                     text=f"{top_words_array[1][0]} and bought {top_words_array[1][1]} times by our customers",
                                     font=("Arial", 12))

        reco_items3_label = tk.Label(self.master,
                                     text=f"{top_words_array[2][0]} and bought {top_words_array[2][1]} times by our customers",
                                     font=("Arial", 12))


        recommendations_label.pack(pady=20)
        reco_items1_label.pack(pady=20)
        reco_items2_label.pack(pady=20)
        reco_items3_label.pack(pady=20)


        back_button = tk.Button(self.master, text="Go Back", font=("Arial", 12), command=self.go_back)
        back_button.pack(pady=10)

    def go_back(self):
        self.master.withdraw()  # Hide the current screen
        new_screen = tk.Toplevel(self.master)
        main_scene = OpenWindow(new_screen)



if _name_ == "_main_":
    root = tk.Tk()
    app = OpenWindow(root)
    root.mainloop()