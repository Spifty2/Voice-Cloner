from qwen_tts import Qwen3TTSModel
import soundfile as sf
import tkinter as tk
import time 
from pathlib import Path
import shutil

TTS_MODEL = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
language = "en"

window = tk.Tk()
window.title("YouSpeak - Voice Cloning")
window.geometry("800x600")
window.configure(bg="#7b0416")
tk.Label(window, text="Enter text to clone voice:").pack(pady=5)
voice_list = tk.Listbox(window, height=5, selectmode=tk.SINGLE)
add_button = tk.Button(window, text="Add New Voice", command=lambda: open_add_voice_window())
text_entry = tk.Entry(window, width=50)
text_entry.pack(pady=5)
enter_button = tk.Button(window, text="Clone Voice", command=lambda: clone_voice(text_entry.get()))
enter_button.pack(pady=5)




BASE_DIR = Path(__file__).resolve().parent
Sounds_DIR = BASE_DIR / "Sounds"
Sounds_DIR.mkdir(exist_ok=True)

def open_add_voice_window():
    add_voice_window = tk.Tk()

    add_voice_window.title("Add New Voice")
    add_voice_window.geometry("400x300")
    path_label = tk.Label(add_voice_window, text="Path to reference audio:")
    path_label.pack(pady=5)
    path_entry = tk.Entry(add_voice_window, width=50)
    path_entry.pack(pady=5)
    transcript_label = tk.Label(add_voice_window, text="Exact transcript of that audio:")
    transcript_label.pack(pady=5)
    transcript_entry = tk.Entry(add_voice_window, width=50)
    transcript_entry.pack(pady=5)
    enter_name_label = tk.Label(add_voice_window, text="Name for new voice:")
    enter_name_label.pack(pady=5)
    enter_name_entry = tk.Entry(add_voice_window, width=50)
    enter_name_entry.pack(pady=5)
    finish_button = tk.Button(add_voice_window, text="Finish", command=lambda: add_sound(enter_name_entry.get(), path_entry.get(), transcript_entry.get()))
    finish_button.pack(pady=20)

    add_voice_window.mainloop()

def list_sounds():
    return sorted(
         p.name for p in Sounds_DIR.iterdir()
        if (p / "ref.wav").exists() and (p / "ref.txt").exists()
    )

def list_outputs():
    return sorted(
        p.name for p in BASE_DIR.iterdir()
        if p.suffix == ".wav"
    )


def list_voices():
    return sorted(
        p.name for p in Sounds_DIR.iterdir()
        if (p / "ref.wav").exists() and (p / "ref.txt").exists()
    )

voice_list.insert(tk.END, *list_voices())


def load_sound(name):
    folder = Sounds_DIR / name
    ref_audio = str(folder / "ref.wav")
    ref_text = (folder / "ref.txt").read_text(encoding="utf-8").strip()
    return ref_audio, ref_text


def add_sound(name, audio_path, transcript):
    name = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()
    folder = Sounds_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy(audio_path, folder / "ref.wav")
    (folder / "ref.txt").write_text(transcript.strip(), encoding="utf-8")
    return name

voices = list_voices()
print("Voices:", ", ".join(voices) if voices else "(none yet)")
choice = input("Voice name (or 'new' to add one): ").strip()

if choice.lower() == "new" or choice not in voices:
    name = input("Name for new voice: ").strip()
    audio = input("Path to reference audio: ").strip('"')
    text = input("Exact transcript of that audio: ")
    choice = add_sound(name, audio, text)

ref_audio_path, ref_text = load_sound(choice)

def clone_voice(text):
    global start_time
    start_time = time.time()
    wavs, sr = TTS_MODEL.generate_voice_clone(
        text=text,
        language="English",          
        ref_audio=ref_audio_path,
        ref_text=ref_text,
    )
    end_time = time.time()
    print(f"Voice cloning completed in {end_time - start_time:.2f} seconds.")
    sf.write(f"output_{choice}.wav", wavs[0], samplerate=sr)

window.mainloop()

