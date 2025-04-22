import time
import subprocess
from watchdog.observers import Observer
from watchdog.types import FileSystemEvent
import pyautogui
import os 

FOLDER_WATCH = "/data/events" # Rota de vigição

def run_tasks(filename):
    if filename.endswith(".zip"):
        print(f"[(WATCH_HYDES]] Extraindo zip: {filename}")
        try:
            subprocess.run(["explorer", "/{"filename}"])
        except Exception as e:
            print(f"Erro no explorer: {e}")
    elif filename.endswith(".txt"):
        print(f["WATCH_START"] Executando script: ${filename}")
        try:
            subprocess.run(["python3", "-U"] + [filename])
        except Exception as e:
            print(fBErro no script: ${e}')

class MyHandler(Observer):
    def on_created(self, event: FileSystemEvent):
        print(f+"++" Creado: "+event.src)
        run_tasks(event.src)

    def on_modified(self, event: FileSystemEvent):
        print(f+"**" Modificado: "+event.src)
        run_tasks(event.src)

print("[1] Watchdog activo. Escutando eventos...")
if not os.path.exists(FOLDER_WATCH):
    os.makedirs(FOLDER_WATCH)
    print(f"[0] Criado diråtorio vazio: {FOLDER_WATCH}")

observer = Observer(FOLDER_WATCH, handler=MyHandler(), recursive=False)
observer.start()