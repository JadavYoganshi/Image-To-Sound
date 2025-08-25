from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from pathlib import Path
import os
from werkzeug.utils import secure_filename
import uuid
from PIL import Image
import pytesseract
from gtts import gTTS
import pyttsx3
from shutil import which
import time
from langdetect import detect
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# ---------- Configuration ----------
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "webp"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024   # 10 MB
CLEANUP_OLDER_SECONDS = 60 * 60         # 1 hour

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["OUTPUT_FOLDER"] = str(OUTPUT_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = "replace-this-with-a-random-secret"

# ---------- Tesseract detection ----------
def find_tesseract():
    exe = which("tesseract")
    if exe:
        return exe
    common = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for p in common:
        if Path(p).exists():
            return str(p)
    return None

tess = find_tesseract()
if tess:
    pytesseract.pytesseract.tesseract_cmd = tess
else:
    print("⚠ WARNING: Tesseract not found. Update the path manually if needed.")

# ---------- Helper functions ----------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files(folder: Path, older_than_seconds=CLEANUP_OLDER_SECONDS):
    now = time.time()
    for f in folder.iterdir():
        if f.is_file():
            try:
                if now - f.stat().st_mtime > older_than_seconds:
                    f.unlink()
            except Exception:
                pass

# Mapping detected language -> gTTS code
LANG_MAP = {
    "en": "en",   # English
    "hi": "hi",   # Hindi
    "gu": "gu",   # Gujarati
    # Sanskrit handled separately (transliteration)
}

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cleanup_old_files(UPLOAD_FOLDER)
        cleanup_old_files(OUTPUT_FOLDER)

        if "image" not in request.files:
            flash("No file part in the request.")
            return redirect(request.url)

        file = request.files["image"]
        if file.filename == "":
            flash("No file selected.")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Unsupported file type. Allowed: " + ", ".join(sorted(ALLOWED_EXTENSIONS)))
            return redirect(request.url)

        orig = secure_filename(file.filename)
        ext = orig.rsplit(".", 1)[1].lower()
        uid = uuid.uuid4().hex
        image_name = f"{uid}.{ext}"
        image_path = UPLOAD_FOLDER / image_name
        file.save(image_path)

        # Validate image
        try:
            img = Image.open(image_path)
        except Exception:
            flash("Uploaded file is not a valid image.")
            image_path.unlink(missing_ok=True)
            return redirect(request.url)

        # OCR with English + Hindi + Gujarati + Sanskrit
        try:
            text = pytesseract.image_to_string(img, lang="eng+hin+guj+san")
        except Exception as e:
            flash("OCR failed: " + str(e))
            return redirect(request.url)

        cleaned_text = " ".join(text.split())
        if not cleaned_text.strip():
            flash("No text detected in the image.")
            return redirect(request.url)

        # Detect language
        try:
            detected = detect(cleaned_text)
            print(f"Detected language: {detected}")
        except Exception:
            detected = "en"

        # Get selected TTS engine (default gTTS)
        engine_choice = request.form.get("engine", "gtts")

        # Convert to speech
        mp3_name = f"{uid}.mp3"
        mp3_path = OUTPUT_FOLDER / mp3_name
        try:
            if detected == "sa":  # Sanskrit
                # Convert Devanagari -> IAST
                text_iast = transliterate(cleaned_text, sanscript.DEVANAGARI, sanscript.IAST)
                print("Sanskrit (IAST):", text_iast)
                if engine_choice == "pyttsx3":
                    engine = pyttsx3.init()
                    engine.save_to_file(text_iast, str(mp3_path))
                    engine.runAndWait()
                else:
                    tts = gTTS(text=text_iast, lang="en")  # use English TTS for IAST
                    tts.save(str(mp3_path))
            else:
                lang_code = LANG_MAP.get(detected, "en")  # fallback to English
                if engine_choice == "pyttsx3":
                    engine = pyttsx3.init()
                    engine.save_to_file(cleaned_text, str(mp3_path))
                    engine.runAndWait()
                else:
                    tts = gTTS(text=cleaned_text, lang=lang_code)
                    tts.save(str(mp3_path))
        except Exception as e:
            flash("Text-to-speech failed: " + str(e))
            return redirect(request.url)

        return render_template(
            "result.html",
            text=cleaned_text,
            audio_url=url_for("get_output", filename=mp3_name),
            engine=engine_choice,
            lang=detected
        )

    return render_template("index.html")

@app.route("/outputs/<path:filename>")
def get_output(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=False)

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
