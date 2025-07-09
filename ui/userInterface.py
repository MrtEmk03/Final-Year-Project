import tkinter as tk
from tkinter import scrolledtext

class MovieChatbotUI:
    def __init__(self, root, handle_input_callback):
        self.root = root
        self.root.title("Movie Recommendation Chatbot")

        #Set the window to full screen and allow resizing
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        #Apply dark mode colors
        bg_color = "#1e1e1e"
        text_color = "#ffffff"
        input_bg_color = "#2e2e2e"
        button_bg_color = "#0077cc"

        self.root.configure(bg=bg_color)

        #Chat history(scrollable text area)
        self.chat_history = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            state="normal",
            bg=bg_color,
            fg=text_color,
            font=("Helvetica", 12),
            relief="solid",
            borderwidth=1
        )
        self.chat_history.pack(padx=10, pady=10, fill="both", expand=True)

        #Set "ScreenScout " and "You" messages to different colors
        self.chat_history.tag_config("ScreenScout ", foreground="#1E90FF", font=("Helvetica", 12, "bold"))
        self.chat_history.tag_config("You", foreground="#FFD700", font=("Helvetica", 12))

        # **GREET USER WITH INSTRUCTIONS**
        greeting_message = (
            "Welcome to MovieBot! (Default language: English)\n"
            "To get movie recommendations, simply type your movie preferences.\n"
            "\n\n"
            "MovieBot'a hoş geldiniz!\n"
            "Film önerileri almak için, film tercihlerinizi yazın.\n"
        )
        self.display_message("ScreenScout ", greeting_message)

        #Input area
        input_frame = tk.Frame(root, bg=bg_color)
        input_frame.pack(padx=10, pady=10, fill="x")

        #Input box
        self.user_entry = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            bg=input_bg_color,
            fg=text_color,
            font=("Helvetica", 12),
            relief="solid",
            borderwidth=1
        )
        self.user_entry.pack(side="left", padx=5, pady=5, fill="both", expand=True)

        #Send button
        send_button = tk.Button(
            input_frame,
            text=" Send ",
            command=handle_input_callback,
            bg=button_bg_color,
            fg=text_color,
            font=("Helvetica", 11, "bold"),
            relief="raised",
            borderwidth=0,
            padx=10,
            pady=5
        )
        send_button.pack(side="left", padx=5, pady=5)

        #Bind Enter key to the handle_input_callback function
        self.user_entry.bind("<Return>", lambda event: self.handle_enter_key(event, handle_input_callback))

    def get_user_input(self):
        """Get the current text from the input field."""
        user_input = self.user_entry.get("1.0", tk.END).strip()
        self.user_entry.delete("1.0", tk.END)  #Clear the input field
        return user_input

    def display_message(self, sender, message):
        """Display a message in the chat history."""
        if sender.lower() == "ScreenScout ":
            self.chat_history.insert(tk.END, f"ScreenScout : {message}\n\n", "ScreenScout ")
        elif sender.lower() == "you":
            self.chat_history.insert(tk.END, f"You: {message}\n\n", "You")
        else:
            self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_history.see(tk.END)  #Scroll to latest message

    def handle_enter_key(self, event, handle_input_callback):
        """Handle the Enter key to submit user input."""
        handle_input_callback()
        return "break"  #Prevent default newline behavior in Text widget
