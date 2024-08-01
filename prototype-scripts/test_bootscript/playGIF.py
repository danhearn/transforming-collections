import tkinter as tk
import time 
from PIL import Image, ImageTk

class MyApp(tk.Frame):
    def _int_(self, root):

        super().__init__(
            root,
            bg='WHITE'
        )

        self.main_frame = self
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        self.label_gif1 = tk.Label(
            self.main_frame,
            bg='WHITE',
            border=0,
            highlightthickness=0
        )
        self.label_gif1(column=0, row=0)
        
    
root = tk.Tk()
root.title('My App')
root.geometry('600x600')
root.resizable(width=False, height=False)

my_app_istance = MyApp(root)

root.mainloop()

#got to 6:31 of this https://www.youtube.com/watch?v=KQ0Dddn6sag