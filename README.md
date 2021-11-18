# Youtube Transcriber

This is a quick and dirty summary of how this works.

This uses Streamlit and AssemblyAI. Consider this a hightly modified version of [their tutorial](https://www.assemblyai.com/blog/how-to-make-a-web-app-that-transcribes-youtube-videos-with-streamlit/). 

## Instructions
* rename configure.py.example to configure.py. Paste in assemblyai key.
* install youtube-dl, ffmpeg, streamlit, and yt-dlp. technically youtube-dl was replaced with yt-dlp but i haven't removed it as a requirement yet so it would probably fail without it. i use pipenv instead of just pip so the following will be using that
* run "pipenv shell" to get into the environment then run "streamlit run ytt.py". 
* Go to site listed on screen
* paste in youtube video, it should show below
* adjust start and end time. they must be in hh:mm:ss format. if you leave the end time blank it just transcribes to the end. If you just want to transcribe the entire video just leave the defaults. 
* click the submit for transcription button and wait. It could take awhile. It downloads the audio from youtube using yt-dlp, converts it to mp3 using ffmpeg, and then uploads it to assemblyai and starts the transcription. I am using the new auto chapters feature.
* once that's done it will say it's been submitted. you can click on the check progress. The transcription can take up to 30% of the time of the video. 
* once the status is complete, it will download the transcript and the paragraphs and save them locally. It will also generate a youtube chapters link to paste in your youtube description. And finally it generates a markdown file with chapters and links to timecodes for the youtube embed using the youtube iframe api.

This is pretty specialized to our use case. I am happy to answer questions but my time is limited so I don't guarentee support of any kind. This was a quick job and it's messy. If I get time I'd like to clean it up. 