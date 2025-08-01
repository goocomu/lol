# !~ > fuck Society < ~!
# ---------------------------
# The most dangerous DoS tool
# ---------------------------
# Author : goocomu

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time

# Setup
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Fsociety DDoS Tool")
app.geometry("600x400")

flashing = False
flashing_label = None

def start_ddos():
    target = ddos_entry.get()
    if not target:
        messagebox.showwarning("Input Error", "Enter a website or IP address.")
        return

    
    # Start flashing full-screen effect
    app.after(500, go_fullscreen_and_flash)

def go_fullscreen_and_flash():
    global flashing_label, flashing
    flashing = True

    app.attributes("-fullscreen", True)
    flashing_label = ctk.CTkLabel(app, text="your files have been ENCRYPTED!!!!!", font=("Arial Black", 50), text_color="red")
    flashing_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def flash_loop():
        colors = ["black", "red"]
        i = 0
        while flashing:
            app.configure(fg_color=colors[i % 2])
            flashing_label.configure(text_color=colors[(i + 1) % 2])
            i += 1
            time.sleep(0.1)

    threading.Thread(target=flash_loop, daemon=True).start()

def stop_app(event=None):
    global flashing
    flashing = False
    app.destroy()

# Input section
ddos_entry = ctk.CTkEntry(app, placeholder_text="Target website or IP (e.g. example.com)", width=450)
ddos_entry.pack(pady=40)

start_btn = ctk.CTkButton(app, text="Start DDoS", command=start_ddos)
start_btn.pack(pady=20)

# ESC to exit
app.bind("<Escape>", stop_app)

# Run the app
app.mainloop()

# FULLY skidded, Credits to @jonskujonskuu on github

