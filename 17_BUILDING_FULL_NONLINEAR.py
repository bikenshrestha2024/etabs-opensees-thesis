"""Open cited building research setup; does not approve the production model."""
from pathlib import Path
import sys
import tkinter as tk

ROOT = Path(__file__).resolve().parent


if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
    from components.ui.building_exploratory_gui import launch

    root = tk.Tk()
    root.withdraw()
    win = launch(root, ROOT / 'Saved_Project_V156')
    win.protocol('WM_DELETE_WINDOW', root.destroy)
    root.mainloop()
