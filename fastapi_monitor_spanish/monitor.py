import os
import time
import requests
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import datetime
from pydub.utils import mediainfo

spanishService_url = 'http://localhost:9001/transcribe'

spanishAudio_folder_path = 'spanish/spanish_pickup/'

spanishResult_folder_path = 'spanish/spanish_results/'

spanishCompleted_folder_path = 'spanish/spanish_completed/'

spanish_counter = 0
log_filename = './spanish/log.txt'

# Check and create directories if they do not exist
for path in [spanishAudio_folder_path, spanishResult_folder_path, spanishCompleted_folder_path]:
    os.makedirs(path, exist_ok=True)

class SpanishDirectoryHandler(FileSystemEventHandler):
    def on_created(self, event):
        global spanish_counter
        spanish_counter += 1
        date_time_str = datetime.datetime.now().strftime("%Y_%m_%d")
        new_filename = f"S{str(spanish_counter).zfill(3)}_{date_time_str}.wav"
        os.rename(event.src_path, os.path.join(spanishAudio_folder_path, new_filename))
        self.process(event, spanishService_url, spanishResult_folder_path, new_filename)


    def process(self, event, service_url, result_folder, filename):
        self._process_audio(event, service_url, result_folder, filename)
    
    def _process_audio(self, event, service_url, result_folder, filename):
        
        filepath = os.path.join(os.path.dirname(event.src_path), filename)
        start_time = datetime.datetime.now()

        with open(filepath, 'rb') as f, open(log_filename, 'a') as log_file:
            audio_info = mediainfo(filepath)
            audio_length = float(audio_info['duration'])
            audio_size = os.path.getsize(filepath)

            print(f"Detected new file: {filename}. Transcribing......")
            log_file.write(f"\n[{start_time.strftime('%Y-%m-%d %H:%M:%S')}]\n"
                        f"Detected new file: {filename}\n"
                        f"Size: {audio_size / 1024} KB\n"
                        f"Duration: {audio_length} seconds\n"
                        f"Transcribing...\n")

            r = requests.post(service_url, files={'file': f})
            end_time = datetime.datetime.now()

            if r.status_code == 200:
                print(f"Transcription successful for file {filename}.")
                result_filepath = os.path.join(result_folder, f"{os.path.splitext(filename)[0]}.json")
                with open(result_filepath, 'w') as result_file:
                    json.dump(r.json(), result_file, ensure_ascii=False)

                log_file.write(f"\n[{end_time.strftime('%Y-%m-%d %H:%M:%S')}]\n"
                            f"Transcription successful for file {filename}.\n"
                            f"Status code: {r.status_code}.\n"
                            f"Time taken: {end_time - start_time}.\n")

                shutil.move(filepath, os.path.join(spanishCompleted_folder_path, filename))  # move file to completed directory
                log_file.write(f"File {filename} moved to completed directory.\n\n")
            else:
                print(f"Error occurred during transcription of file {filename}. Status code: {r.status_code}")
                log_file.write(f"\n[{end_time.strftime('%Y-%m-%d %H:%M:%S')}]\n"
                            f"Error occurred during transcription of file {filename}.\n"
                            f"Status code: {r.status_code}.\n"
                            f"Response message: {r.text}.\n\n")


def start_monitoring(path, event_handler):
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    print(f"Started monitoring folder: /spanish/")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_monitoring(spanishAudio_folder_path, SpanishDirectoryHandler())
