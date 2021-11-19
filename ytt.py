import streamlit as st
from configure import auth_key
import youtube_dl
import ffmpeg
import requests
import pprint
from time import sleep
import json
import yt_dlp

if 'status' not in st.session_state:
    st.session_state['status'] = 'waiting for user'
    st.session_state['polling_endpoint'] = ''
    st.session_state['mp3name'] = ''
    st.session_state['duration'] = 0
    st.session_state['upload_url'] = ''
    


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }],
    'ffmpeg-location': './',
    'outtmpl': "./%(id)s.%(ext)s"
}

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
upload_endpoint = "https://api.assemblyai.com/v2/upload"
balance_endpoint = "https://api.assemblyai.com/v2/account"

headers_auth_only = {'authorization': auth_key}
headers = {
    "authorization": auth_key,
    "content-type": "application/json"
}

#polling_endpoint_global = ''

CHUNK_SIZE = 5242880

def get_balance(return_formatted=True):
    response = requests.get(
        balance_endpoint,
        headers=headers_auth_only
    )

    value = response.json()['current_balance']['amount']

    if return_formatted:
        return "${:,.2f}".format(value)
    return value

def milliseconds_to_seconds(milliseconds):
    return milliseconds // 1000

def milliseconds_to_hhmmss(milliseconds):

    hours = 0
    minutes = 0
    seconds = 0

    if (milliseconds >= 3600000):
        hours = milliseconds // 3600000
        milliseconds = milliseconds - (hours * 3600000)
    
    if (milliseconds >=  60000):
        minutes = milliseconds // 60000
        milliseconds = milliseconds - (minutes * 60000)

    if (milliseconds >= 1000):
        seconds = milliseconds // 1000
        milliseconds = milliseconds - (seconds * 1000)

    return "%02i:%02i:%02i" % (hours, minutes, seconds)

def hhmmss_to_milliseconds(hhmmss):
    splitstring = hhmmss.split(":")

    splitlen = len(splitstring)

    hours = 0
    minutes = 0
    seconds = 0

    if (splitlen == 3):
        hours = int(splitstring[0])
        minutes = int(splitstring[1])
        seconds = int(splitstring[2])
    
    if (splitlen == 2):
        minutes = int(splitstring[0])
        seconds = int(splitstring[1])

    milliseconds = (hours * 3600000) + (minutes * 60000) + (seconds * 1000)
    return milliseconds

@st.cache
def transcribe_from_link(link, start_from, end_at):
    _id = link.strip()

    def get_vid(_id):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(_id)

    meta = get_vid(_id)
    save_location = meta['id'] + ".mp3"
    #print(meta)
    st.session_state['duration'] = meta['duration']
    st.session_state['mp3name'] = save_location

    print ('Saved mp3 to ', save_location)

    def read_file(filename):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(CHUNK_SIZE)
                if not data:
                    break
                yield data
    
    upload_response = requests.post(
        upload_endpoint,
        headers=headers_auth_only, data=read_file(save_location)
    )

    audio_url = upload_response.json()['upload_url']
    print('Uploaded to ', audio_url)
    st.session_state['upload_url'] = audio_url

    transcript_request = {
        'audio_url': st.session_state['upload_url'],
        'auto_chapters': True
    }

    transcript_request['audio_start_from'] = hhmmss_to_milliseconds(start_from)

    if (end_at):
        transcript_request['audio_end_at'] = hhmmss_to_milliseconds(end_at)

    print (transcript_request)



    transcript_response = requests.post(
        transcript_endpoint, json=transcript_request, headers=headers
    )

    transcript_id = transcript_response.json()['id']
    polling_endpoint = transcript_endpoint + "/" + transcript_id

    print ("Transcribing at ", polling_endpoint)

    st.session_state['polling_endpoint'] = polling_endpoint
    st.session_state['status'] = 'submitted'
    return
    
   


def get_status(polling_endpoint):
    print(polling_endpoint)
    polling_response = requests.get(polling_endpoint, headers=headers)
    st.session_state['status'] = polling_response.json()['status']

def refresh_state():
    st.session_state['status'] = 'submitted'

def format_transcript(mp3name):

    with open(st.session_state['mp3name'] + ".youtube_chapters.txt", 'a') as ww:
        with open(st.session_state['mp3name'] + ".markdown", 'a') as w:

            w.write("_The following is a computer generated transcript. [Learn more about our automated transcription.](/about-transcription)_\n\n")

            with open(st.session_state['mp3name'] + '.json', 'r') as f:
                jsondata = json.load(f)

                w.write("### Chapters\n")
                ww.write("Chapters\n")
                ww.write("--------------------\n")


                for item in jsondata["chapters"]:
                    print(item)
                    w.write("<a href=\"#\" onclick=\"player.seekTo(" + str(milliseconds_to_seconds(item['start'])) +  ", true);\">" + milliseconds_to_hhmmss(item['start']) + "</a>" + " " + item['headline'] + "  \n")
                    ww.write(milliseconds_to_hhmmss(item['start']) + " " + item['headline'] + "\n")

            with open(st.session_state['mp3name'] + '.paragraphs.json', 'r') as f:
                jsondata = json.load(f)

                w.write("\n### Transcript\n")

                for item in jsondata["paragraphs"]:
                    w.write("<a href=\"#\" onclick=\"player.seekTo(" + str(milliseconds_to_seconds(item['start'])) +  ", true);\">" + milliseconds_to_hhmmss(item['start']) + "</a>" + " " + item['text'] + "\n\n") 

            


st.title("YTT2")

st.sidebar.text("Balance: " + get_balance())

link = st.text_input('Enter YT link', 'https://youtu.be/dccdadl90vs', on_change=refresh_state)

st.video(link)

start_from = st.text_input('Timecode to start at', '00:00:00')

end_at = st.text_input('Timecode to end at')


st.button('Submit for Transcription', on_click=transcribe_from_link, args=(link,start_from, end_at))


#st.write("Video Duration is ", st.session_state['duration'])

st.text('The transcription is ' + st.session_state['status'])

#polling_endpoint = transcribe_from_link(link)  

st.button('check_status', on_click=get_status, args=(st.session_state['polling_endpoint'], ))

transcript = ''
if st.session_state['status'] == 'completed':
    polling_response = requests.get(st.session_state['polling_endpoint'], headers=headers)
    transcript = polling_response.json()['text']
    with open(st.session_state['mp3name'] + '.json', 'w') as f:
        json.dump(polling_response.json(), f)
    
    paragraph_response = requests.get(st.session_state['polling_endpoint'] + '/paragraphs', headers=headers)
    with open(st.session_state['mp3name'] + '.paragraphs.json', 'w') as f:
        json.dump(paragraph_response.json(), f)

    format_transcript(st.session_state['mp3name'])







st.markdown(transcript)