import time
import sys
import threading
import pyperclip
import tkinter as tk
from openai import OpenAI

# Koboldcpp Client Config
client = OpenAI(
    base_url="http://localhost:5001/v1", 
    api_key="lm-studio" 
)

def translate_text(text):
    # Shortened system prompt to reduce prompt processing time
    system_prompt = (
        "You are an expert Japanese to English visual novel translator. "
        "Translate the text naturally. Output ONLY the English translation. "
        "Do not repeat the Japanese source."
    )
    
    try:
        # Changed from completions.create to chat.completions.create
        response = client.chat.completions.create(
            model="koboldcpp",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=80,
            extra_body={
                "stop": ["\n", "<|eot_id|>", "<|end_of_text|>"] # Hard stop triggers to save processing cycles
            }
        )
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            return "[Translation Error: Koboldcpp returned an empty response]"
            
    except Exception as e:
        return f"[Translation Error: Unable to parse model response]"



# --- TEXT FILTERING FUNCTION ---
def should_ignore(text):
    clean_text = text.strip()
    
    # Ignore if text is too long (usually a massive menu dump/save configuration)
    if len(clean_text) > 120: 
        return True
        
    # Ignore if it contains common game system words (stats, configuration, items, levels)
    system_keywords = ["Config", "Save", "Lv", "HP", "MP", "Llama"]
    if any(keyword in clean_text for keyword in system_keywords):
        return True
        
    return False

# --- UI WINDOW CLASS WITH THEME ---
class FloatingOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Translation Overlay")
        
        # 1. Match the Game's theme
        GAME_BLUE = "#1d2d50"
        BORDER_WHITE = "#e1e4f2" 
        
        self.root.configure(bg=GAME_BLUE)
        self.root.attributes("-topmost", True)
        self.root.geometry("520x130+100+100") # Adjusts the ui
        self.root.overrideredirect(True) 
        
        # 2. Recreate the Game's Double-Border Look using a Frame
        border_frame = tk.Frame(
            self.root, 
            bg=GAME_BLUE, 
            highlightbackground=BORDER_WHITE, 
            highlightcolor=BORDER_WHITE, 
            highlightthickness=4, # The thickness of the white border
            bd=0
        )
        border_frame.pack(expand=True, fill="both", padx=4, pady=4)
        
        # 3. Add the Dialogue Text Label
        self.label = tk.Label(
            border_frame, 
            text="Waiting for Textractor...", 
            font=("Arial", 12, "bold"), 
            fg="white", 
            bg=GAME_BLUE, 
            wraplength=480, 
            justify="left",
            anchor="nw"
        )
        self.label.pack(expand=True, fill="both", padx=15, pady=12)
        
        # Draggable bindings
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)
        
        # Right-click context menu to Exit
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Exit", command=self.quit_app)
        self.root.bind("<Button-3>", self.show_menu)


    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def update_text(self, text):
        self.label.config(text=text)

    def quit_app(self):
        self.root.destroy()
        sys.exit()

# --- BACKGROUND MONITORING THREAD ---
def monitor_clipboard(overlay):
    last_text = pyperclip.paste()
    while True:
        try:
            current_text = pyperclip.paste()
            if current_text != last_text and current_text.strip():
                last_text = current_text
                
                # Check if this text should be skipped (the menu junk)
                if should_ignore(current_text):
                    continue
                
                print(f"\n JP: {current_text.strip()}")
                translation = translate_text(current_text)
                print(f"EN: {translation}")
                
                # Push the translation to our floating UI window
                overlay.root.after(0, overlay.update_text, translation)
                
            time.sleep(0.2)
        except Exception:
            pass

if __name__ == "__main__":
    app = FloatingOverlay()
    
    # Start the clipboard monitor as a separate background task so the window doesn't freeze
    monitor_thread = threading.Thread(target=monitor_clipboard, args=(app,), daemon=True)
    monitor_thread.start()
    
    app.root.mainloop()
