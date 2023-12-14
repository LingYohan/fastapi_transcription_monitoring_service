This repo is a mointoring script which looks for audio files in a directory, and once it detects any audio file, it will be sent for the fastapi endpoint for transcription and then the output for each respective audio files will be stored in a seperate folder. 

each folder contains the following files:

-- requirements.txt -> all the required python packages
-- monitor.py -> monitoring script
-- service.py -> fastAPI service which uses the whisper model for transcription (also masks credit card information) 
