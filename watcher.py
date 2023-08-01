import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class OnMyWatch:
    def __init__(self):
        self.observer = Observer()
        self.watchDirectory = "."
        self.bot_process = None
        self.start_bot()

    def run(self):
        event_handler = Handler(self)
        self.observer.schedule(
            event_handler, self.watchDirectory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            print("🛑 Observer Stopped 🛑")

        self.observer.join()

    def start_bot(self):
        print("🎵 Starting the music bot... 🎵")
        delete_txt_and_log_files()
        self.bot_process = subprocess.Popen(
            ['./.venv/Scripts/python', 'music_bot.py'])

    def stop_bot(self):
        if self.bot_process is not None:
            print("⏹️ Terminating the music bot process (PID: %d) ⏹️" %
                  self.bot_process.pid)
            self.bot_process.terminate()
            self.bot_process = None


class Handler(FileSystemEventHandler):
    def __init__(self, on_my_watch):
        self.on_my_watch = on_my_watch
        self.last_trigger = time.time()

    def on_any_event(self, event):
        now = time.time()
        if now - self.last_trigger > 5:
            print(f'🔍 Watchdog received {event.event_type} event - {event.src_path}. 🔍')
            if event.event_type == 'modified' and (event.src_path.find('.py') != -1 or event.src_path.find('error_logger.py') != -1) :
                # Stop the music bot process
                self.on_my_watch.stop_bot()

                # Start the music bot process again
                self.on_my_watch.start_bot()
            self.last_trigger = now

# Function to delete all .txt and .log files in the current directory
def delete_txt_and_log_files():
    current_directory = os.getcwd()
    for file_name in os.listdir(current_directory):
        if file_name.find('requirements.txt') != -1:
            return
        if file_name.endswith('.txt') or file_name.endswith('.log') :
            file_path = os.path.join(current_directory, file_name)
            try:
                os.remove(file_path)
                print(f"❌ Deleted file: {file_name} ❌")
            except Exception as e:
                print(f"⚠️ Error deleting file: {file_name} - {e} ⚠️")



if __name__ == '__main__':
    watch = OnMyWatch()
    watch.run()
