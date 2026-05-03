from ui.main_window import AppGranjaPando
import tkinter as tk
from database import db_local

if __name__ == "__main__":
    db_local.inicializar_db() 
    root = tk.Tk()
    app = AppGranjaPando(root)
    root.mainloop()