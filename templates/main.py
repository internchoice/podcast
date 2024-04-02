
from flask import Flask, render_template, request, send_file
from pytube import YouTube
import assemblyai as aai
from transformers import pipeline, BartTokenizer, BartForConditionalGeneration
from configure import assembly_ai_api_key
import os
import shutil
import pyttsx3

app = Flask(__name__)

# Initialize BART tokenizer and model
tokenizer_path = "tokenizer-SCOE24-PG16"
model_path = "bart-SCOE24-PG16"
tokenizer = BartTokenizer.from_pretrained(tokenizer_path)
model = BartForConditionalGeneration.from_pretrained(model_path)

# Initialize summarization pipeline
summarization_pipeline = pipeline("summarization", model=model, tokenizer=tokenizer)

class Transcriber:
    def __init__(self, audio_path, api_key):
        self.audio_path = audio_path
        aai.settings.api_key = api_key
        self.transcriber = aai.Transcriber()

    def transcribe_audio(self):
        if self.audio_path:
            config = aai.TranscriptionConfig(speaker_labels=True)
            transcript = self.transcriber.transcribe(self.audio_path, config=config)
            return transcript.text
        else:
            return "Please provide a valid audio path."

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    link = request.form.get('videoURL')
    try:
        # Download audio from YouTube video
        video = YouTube(link)
        audio_path = video.streams.filter(only_audio=True).first().download()

        # Transcribe audio using AssemblyAI
        transcriber = Transcriber(audio_path, assembly_ai_api_key)
        transcript_text = transcriber.transcribe_audio()

        # Calculate length of transcript
        transcript_length = "transcript_text"

        return render_template('main.html', transcript=transcript_text, transcript_length=transcript_length)
    
    except Exception as e:
        return render_template('main.html', error=f"An error occurred while processing: {str(e)}")

@app.route('/summarize', methods=['POST'])
def summarize():
    transcript_text = request.form.get('transcript')

    try:
        # Generate summary using BART model
        summaries = process_long_text(transcript_text, summarization_pipeline)

        # Process and remove text as described
        merged_summary = ""
        first_occurrence = True
        for summary in summaries:
            # Remove phrases from the summary
            if first_occurrence:
                new_summary = summary
                first_occurrence = False
            else:
                new_summary = summary.replace("In this episode, ", "")
            # Concatenate summaries
            merged_summary += new_summary + " "

        # Calculate length of summary
        summary_length = "merged_summary"

        # Generate audio from summarized text
        engine = pyttsx3.init()
        engine.save_to_file(merged_summary, 'summary_audio.mp3')
        engine.runAndWait()

        return render_template('main.html', summary=merged_summary, summary_length=summary_length, transcript=transcript_text)
    
    except Exception as e:
        return render_template('main.html', error=f"An error occurred while processing: {str(e)}")

@app.route('/get_audio')
def get_audio():
    return send_file('summary_audio.mp3', as_attachment=True)

def process_long_text(long_text, summarization_pipeline, max_seq_length=1024):
    # Split the long text into overlapping segments
    stride = max_seq_length
    segments = []

    for start in range(0, len(long_text), stride):
        end = start + max_seq_length
        segment_text = long_text[start:end]

        # Generate summaries for each segment using the summarization pipeline
        segment_summary = summarization_pipeline(segment_text, max_length=100, min_length=10, do_sample=False)[0]
        segments.append(segment_summary)

    # Extract the summaries from the collected results
    summaries = [segment['summary_text'] for segment in segments]

    return summaries

if __name__ == "__main__":
    app.run(debug=True)




