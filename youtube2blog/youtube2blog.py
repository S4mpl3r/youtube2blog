import os
import re
from sys import platform
from time import time

from colored import cprint
from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv
from groq import Groq
from pytube import YouTube

load_dotenv()

# API KEYS ===============================================================
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# CONSTANTS ==============================================================
LLM_NAME = "mixtral-8x7b-32768"  # Groq llm model
SPEECH_MODEL_EN = "nova-2"  # for english audio
SPEECH_MODEL = "whisper-large"  # for any other audio
AUDIO_LANGUAGE = "english"  # the language of the audio

# directory where prompts are stored
PROMPT_ROOT = "./prompts/"
# directory where audio files are stored
AUDIO_ROOT = "./audio_files/"
# directory where audio transcripts are stored
TRANSCRIPT_ROOT = "./audio_transcripts/"

CLEAR = "clear" if platform == "linux" else "cls"  # clear console command
# Banner =================================================================
BANNER = """
__  __               __          __          ___    ____   __             
\ \/ /____   __  __ / /_ __  __ / /_   ___  |__ \  / __ ) / /____   ____ _
 \  // __ \ / / / // __// / / // __ \ / _ \ __/ / / __  |/ // __ \ / __ `/
 / // /_/ // /_/ // /_ / /_/ // /_/ //  __// __/ / /_/ // // /_/ // /_/ / 
/_/ \____/ \__,_/ \__/ \__,_//_.___/ \___//____//_____//_/ \____/ \__, /  
                                                                 /____/   
"""
# ========================================================================


class Utility:
    """Some utility and helper functions."""

    def download_youtube_audio(url: str) -> str:
        """Downloads the audio of a youtube video."""
        cprint("[+] Downloading youtube audio...", "light_green")
        result_path = (
            YouTube(url)
            .streams.filter(only_audio=True)
            .order_by("abr")
            .desc()
            .first()
            .download(output_path=AUDIO_ROOT)
        )
        cprint("[+] Download complete.", "light_green")
        return result_path

    def save_to_file(path: str, text: str) -> None:
        """Saves text to file."""
        if not os.path.isdir(TRANSCRIPT_ROOT):
            os.mkdir(TRANSCRIPT_ROOT)

        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def pretty_print_tags(string: str) -> None:
        """Prints the tags in a readable way."""
        pattern = r"<li>(.*?)</li>"

        matches = re.findall(pattern, string, re.DOTALL)
        cprint("\n<list>", "light_yellow")
        for i, match in enumerate(matches):
            cprint("    <li>", "light_yellow", end="")
            cprint(f"{i+1}. {match}", end="")
            cprint("</li>", "light_yellow")
        cprint("</list>", "light_yellow")

    def pretty_print(string: str, tag: str) -> None:
        """Prints in a readable way."""
        cprint(f"<{tag}>", "light_yellow")
        print(string)
        cprint(f"</{tag}>", "light_yellow")


class Audio2Text:
    """This class handles everything related to turning audio to text."""

    def __init__(self) -> None:
        self.deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        self.groq = Groq(api_key=GROQ_API_KEY)
        self.from_youtube = False

    def get_audio_file_path(self):
        """Returns the audio file path."""
        if self.from_youtube:
            url = input("Enter full url: ")
            filepath = Utility.download_youtube_audio(url)
        else:
            filename = input("Enter the audio file name: ")
            filepath = os.path.join(AUDIO_ROOT, filename)

        return filepath

    def transcribe_audio(
        self, language: str = AUDIO_LANGUAGE, save_to_file: bool = True
    ) -> str:
        """Transcribes an audio file."""
        filepath = self.get_audio_file_path()

        with open(filepath, "rb") as buffer_data:
            payload = {"buffer": buffer_data}

            if language == "english":
                options = PrerecordedOptions(
                    smart_format=True, model=SPEECH_MODEL_EN, language="en-US"
                )
            else:
                options = PrerecordedOptions(
                    smart_format=True, model=SPEECH_MODEL, language=language
                )

            cprint("[+] Requesting transcript...", "light_green")
            response = self.deepgram.listen.prerecorded.v("1").transcribe_file(
                payload, options
            )
            transcript = response["results"]["channels"][0]["alternatives"][0][
                "transcript"
            ]
            cprint("[+] Transcription complete.", "light_green")

        if save_to_file:
            filename = filepath.split("/")[-1].split(".")[0] + "_transcript.txt"
            Utility.save_to_file(
                path=os.path.join(TRANSCRIPT_ROOT, filename), text=transcript
            )

        return transcript

    def get_tags(self, transcript: str) -> str:
        """Extracts meaningful tags from a given text."""
        with open(os.path.join(PROMPT_ROOT, "tag_prompt.txt"), "r") as f:
            system_prompt = f.read()

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"transcript:\n{transcript}",
            },
        ]
        cprint("[+] Getting tags...", "light_blue")
        chat_completion = self.groq.chat.completions.create(
            messages=messages,
            model=LLM_NAME,
            temperature=0.1,
            max_tokens=512,
        )
        cprint("[+] Getting tags done.", "light_blue")

        return chat_completion.choices[0].message.content

    def get_blog_post(self, transcript: str) -> str:
        """Generates a blog post from a given text."""
        with open(os.path.join(PROMPT_ROOT, "blog_prompt.txt"), "r") as f:
            system_prompt = f.read()

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"reference text:\n{transcript}",
            },
        ]
        cprint("[+] Writing blog post...", "light_blue")
        chat_completion = self.groq.chat.completions.create(
            messages=messages,
            model=LLM_NAME,
            temperature=0.5,
            max_tokens=8000,
        )
        cprint("[+] Writing done.", "light_blue")

        return chat_completion.choices[0].message.content


def main() -> None:
    a2t = Audio2Text()

    cprint(BANNER, "indian_red_1c")
    cprint("What do you want to do?")
    cprint("1) Write blog post\n2) Get tags\n3) Get transcript\n4) Exit", "light_cyan")
    opt = input("Enter an option (1-4): ").strip().lower()
    if opt == "4":
        exit(0)
    if opt not in [*"1234"]:
        cprint("Not a valid option, try again.", "red")
        exit(1)

    os.system(CLEAR)
    cprint("Choose the audio:")
    cprint("1) From youtube video\n2) From local file", "light_cyan")
    opt2 = input("Enter an option (1-2): ").strip().lower()
    if opt2 not in [*"12"]:
        cprint("Not a valid option, try again.", "red")
        exit(1)
    os.system(CLEAR)

    a2t.from_youtube = True if opt2 == "1" else False

    start = time()
    transcript = a2t.transcribe_audio()
    if opt == "1":
        result = a2t.get_blog_post(transcript)
        Utility.pretty_print(result, "blog")
    elif opt == "2":
        result = a2t.get_tags(transcript)
        Utility.pretty_print_tags(result)
    elif opt == "3":
        Utility.pretty_print(transcript, "transcript")

    end = time()
    cprint(f"\nTime taken: {end-start:.4f} s", "light_red")


if __name__ == "__main__":
    main()
