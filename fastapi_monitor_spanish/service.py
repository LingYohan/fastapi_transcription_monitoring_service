from fastapi import FastAPI, UploadFile, HTTPException, File
from pydantic import BaseModel
import whisper
import soundfile as sf
import numpy as np
from tempfile import NamedTemporaryFile
import os, re
import librosa
import datetime

start_time = datetime.datetime(2023, 8, 4)

end_time = start_time + datetime.timedelta(days=15)



model = whisper.load_model("medium")

app = FastAPI()


def creditCardinfo(sentence):
    
    # Removes non-digit characters
    clean_sentence = re.sub(r'\D', '', sentence)

    # Checks if there are exactly 16 digits in the cleaned sentence
    if len(clean_sentence) == 16:
        return clean_sentence
    else:
        return False


def reformatAudio(audioPath):
    data, sr = librosa.load(audioPath)
    
    data = librosa.resample(data, orig_sr=sr, target_sr=16000)
    
    data = librosa.to_mono(data)
    
    return data
    


@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    
    if not start_time <= datetime.datetime.now() <= end_time:
        return {"text": "Service expired. Please contact +91 89712 49091 for further details"}
    
    transcripts = []
    timestamps = []
    with NamedTemporaryFile(delete=False) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
    
    audio_path = temp_file.name
    
    data = reformatAudio(audio_path)

    transcript = model.transcribe(data, word_timestamps=True)
        
    for segment in transcript["segments"]:

        cc = creditCardinfo(segment["text"])
        
        if cc:
            masked_text = ''
            digits_masked = 0
            for ch in segment["text"]:
                if ch.isdigit() and digits_masked < 16:
                    masked_text += 'x'
                    digits_masked += 1
                else:
                    masked_text += ch
            segment["text"] = masked_text
            transcripts.append(segment["text"])

            for word in segment["words"]:

                if cc[0] in word['word'].strip() :
                    timestamps.append(word['start'])
                    break
        else:
            transcripts.append(segment["text"])

    finalTranscription = " ".join(transcripts)
    
    os.remove(audio_path)

    return {"Transcript": finalTranscription, "Timestamps": timestamps}



    



    


    