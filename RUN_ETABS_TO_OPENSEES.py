"""Start the workbench in a fresh process and preserve its startup log."""
import datetime
import os
from pathlib import Path
import runpy
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parent


def _show_startup_error(code, log):
    message = (f"Exit code {code}\nDetails saved in {log}\n\n"
               + log.read_text(encoding="utf-8", errors="replace")[-3000:])
    print(message, file=sys.stderr)
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        try:
            root.withdraw()
            messagebox.showerror("OpenSees startup failed", message, parent=root)
        finally:
            root.destroy()
    except Exception:
        # A broken or unavailable Tk session cannot erase the startup failure.
        return


def main():
    if "--fresh-child" in sys.argv:
        try:
            sys.path.insert(0, str(ROOT))
            runpy.run_path(
                str(ROOT / "ETABS_to_OpenSeesPy_Section_Review_V116_NBC105_Area_NLTHA.py"),
                run_name="__main__",
            )
            return 0
        except BaseException:
            traceback.print_exc()
            return 1

    logs = ROOT / "Startup_Logs"
    logs.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log = logs / f"startup_{stamp}_{os.getpid()}.log"
    env = {**os.environ, "PYTHONPATH": str(ROOT), "PYTHONUTF8": "1",
           "OPENSEES_STARTUP_LOG": str(log)}
    child = None
    with log.open("w", encoding="utf-8") as stream:
        stream.write(f"OpenSees workbench startup | {sys.executable}\nRoot {ROOT}\n")
        stream.flush()
        try:
            child = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--fresh-child"],
                cwd=str(ROOT), env=env, stdout=stream, stderr=subprocess.STDOUT,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError:
            traceback.print_exc(file=stream)
    pointer = log.with_suffix(".latest.tmp")
    pointer.write_text(str(log), encoding="utf-8")
    pointer.replace(logs / "LATEST.txt")
    code = child.wait() if child is not None else 1
    if code:
        _show_startup_error(code, log)
    return code


if __name__ == "__main__":
    sys.exit(main())
