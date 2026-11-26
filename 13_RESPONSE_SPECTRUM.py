from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog

ROOT = Path(__file__).resolve().parent


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title='Select assembled export folder')
    if folder:
        from OpenSees_Model_Response_Spectrum_V132 import launch
        launch(root, folder)
        root.mainloop()
    else:
        root.destroy()
