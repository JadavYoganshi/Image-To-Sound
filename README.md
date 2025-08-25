
# 🖼️ Image to Sound Converter

This Flask web application allows you to upload an image containing text in **English, Hindi, Gujarati, or Sanskrit**, extract the text using **Tesseract OCR**, automatically detect the language, and then generate **speech output (MP3)** using either **Google gTTS** or **pyttsx3**.

---

## 📂 Project Structure

```
Image_to_sound
├── web_app.py          # Main Flask application
├── templates/
│   ├── index.html      # Upload form
│   └── result.html     # Display extracted text + audio player
├── uploads/            # Uploaded images (auto-cleaned)
├── outputs/            # Generated MP3 files (auto-cleaned)
├── requirements.txt    # Dependencies
└── README.md
|__ .gitignore
```
---
## 🚀 Features

- Upload images (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.webp`)
- OCR (Optical Character Recognition) using Tesseract
- Supports **English, Hindi, Gujarati, and Sanskrit**
- Auto-detects language using `langdetect`
- Handles **Sanskrit transliteration** → converts to IAST for better pronunciation
- Choose between:
  - **gTTS (Google Text-to-Speech)** → Natural voice (needs internet)
  - **pyttsx3 (Offline TTS)** → Works without internet
- Audio file (`.mp3`) generated and played directly in the browser
- Automatic cleanup of old uploaded/processed files

---

## 🛠️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/Image_To_Sound.git
cd Image_To_Sound
```

2. **Create virtual environment & install dependencies**

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install Tesseract OCR**

- Download from: https://github.com/tesseract-ocr/tesseract
- On Windows, install to `C:\Program Files\Tesseract-OCR\tesseract.exe`
- Add to PATH or update the path in `web_app.py`

4. **Download traineddata for languages**

Place language files in your Tesseract `tessdata` folder (e.g., `C:\Program Files\Tesseract-OCR\tessdata\`):

- [English (eng)](https://github.com/tesseract-ocr/tessdata/blob/main/eng.traineddata)
- [Hindi (hin)](https://github.com/tesseract-ocr/tessdata/blob/main/hin.traineddata)
- [Gujarati (guj)](https://github.com/tesseract-ocr/tessdata/blob/main/guj.traineddata)
- [Sanskrit (san)](https://github.com/tesseract-ocr/tessdata/blob/main/san.traineddata)

---

## ▶️ Run the App

```bash
python web_app.py
```

Then open your browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📦 requirements.txt

```
Flask
pytesseract
Pillow
gTTS
pyttsx3
langdetect
indic-transliteration
```

---

## 🌐 Usage

1. Upload an image containing **English / Hindi / Gujarati / Sanskrit** text
2. The app will:
   - Extract text (OCR)
   - Detect language
   - For Sanskrit: convert Devanagari → IAST → phonetic-friendly English
   - Generate speech in MP3 format
3. Listen to the result directly in your browser 🎧

---

## ⚠️ Notes

- **gTTS requires internet**. If offline use `pyttsx3` option.
- Sanskrit pronunciation is **approximated** via transliteration. For 100% Vedic Sanskrit pronunciation, a specialized TTS engine is required.
- Uploaded images & audio files are auto-deleted after 1 hour.

---
## 🧑‍💻 Author

Yoganshi Jadav — [GitHub](https://github.com/JadavYoganshi)

---

## 📜 License

MIT License © 2025
