# youtube2blog

![screenshot](https://github.com/S4mpl3r/youtube2blog/blob/main/assets/screenshot.jpg)

youtube2blog offers a seamless solution for transforming any YouTube video, or audio file, into a comprehensive blog post. This tool leverages the power of [Groq](https://groq.com), Mixtral 8x7b, and [Deepgram](https://deepgram.com) to provide a streamlined content creation process.

## Features
- **Video-to-Blog conversion:** Easily convert any YouTube video into a blog post with just the video's URL.
- **Keyword Extraction:** Extract top 10 keywords from a youtube video.
- **Transcription:** Obtain a full transcript of the video for further analysis or content creation.

This tool is not limited to YouTube videos; users can also input their own audio files to generate blog posts, extract keywords, and transcribe content.

## Installation
To use this tool you should obtain Groq and Deepgram API keys. Groq is currently free, and Deepgram provides $200 credit which is more than enough to run this tool.
To install, do the following:
1. Clone the repository:
   ```bash
   git clone https://github.com/S4mpl3r/youtube2blog.git
   ```
2. Create a python environment and activate it. (optional, but highly recommended)
3. Create a .env file in the project root and populate it with your API keys:
   ```bash
   GROQ_API_KEY=<YOUR_KEY>
   DEEPGRAM_API_KEY=<YOUR_KEY>
   ```
3. Install the required packages
   ```bash
   python -m pip install -r requirements.txt
   ```
4. CD into the youtube2blog directory and run the tool:
   ```bash
   cd youtube2blog/
   python youtube2blog.py
   ```

## License
MIT
