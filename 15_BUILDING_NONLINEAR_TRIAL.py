from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog

ROOT = Path(__file__).resolve().parent


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title='Select your assembled export folder')
    if folder:
        from OpenSees_Building_Exploratory_GUI_V138 import launch
        launch(root, folder)
        root.mainloop()
    else:
        root.destroy()
