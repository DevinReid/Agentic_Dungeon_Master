# debug_util.py
DEBUG_MODE = False  # Toggle this globally!

def debug_log(message: str):
    if DEBUG_MODE:
        from typer import secho
        secho(f"DEBUG: {message}", fg="red")
