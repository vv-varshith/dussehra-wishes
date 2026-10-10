
import os
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dussehra-wishes-change-this")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
AUDIO_EXTENSIONS = {"mp3", "wav", "ogg", "m4a"}


def get_media(prefix, allowed_extensions):
    """Find the uploaded image or music file."""
    for filename in sorted(os.listdir(UPLOAD_DIR)):
        if not filename.startswith(prefix + "."):
            continue

        ext = filename.rsplit(".", 1)[-1].lower()

        if ext in allowed_extensions:
            return filename

    return None


def save_upload(file, prefix, allowed_extensions):
    if not file or not file.filename:
        return None

    original_name = secure_filename(file.filename)

    if "." not in original_name:
        raise ValueError("File extension is missing.")

    ext = original_name.rsplit(".", 1)[-1].lower()

    if ext not in allowed_extensions:
        raise ValueError("Unsupported file type: " + ext)

    # Remove previous files of the same type.
    for old_file in os.listdir(UPLOAD_DIR):
        if old_file.startswith(prefix + "."):
            old_path = os.path.join(UPLOAD_DIR, old_file)
            if os.path.isfile(old_path):
                os.remove(old_path)

    new_name = prefix + "." + ext
    file.save(os.path.join(UPLOAD_DIR, new_name))
    return new_name


@app.route("/")
def home():
    image_name = get_media("ammavaru", IMAGE_EXTENSIONS)
    audio_name = get_media("background_music", AUDIO_EXTENSIONS)

    image_url = (
        url_for("static", filename="uploads/" + image_name)
        if image_name else None
    )

    audio_url = (
        url_for("static", filename="uploads/" + audio_name)
        if audio_name else None
    )

    public_url = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")

    return render_template(
        "index.html",
        image_url=image_url,
        audio_url=audio_url,
        public_url=public_url
    )


@app.route("/upload", methods=["POST"])
def upload():
    image = request.files.get("goddess_image")
    music = request.files.get("music_file")

    try:
        if image and image.filename:
            save_upload(image, "ammavaru", IMAGE_EXTENSIONS)
            flash("అమ్మవారి ఫోటో విజయవంతంగా అప్‌లోడ్ అయింది!", "success")

        if music and music.filename:
            save_upload(music, "background_music", AUDIO_EXTENSIONS)
            flash("బ్యాక్‌గ్రౌండ్ పాట అప్‌లోడ్ అయింది!", "success")

        if (
            (not image or not image.filename)
            and (not music or not music.filename)
        ):
            flash("దయచేసి ఫోటో లేదా పాటను ఎంచుకోండి.", "error")

    except (ValueError, OSError) as error:
        flash("Upload error: " + str(error), "error")

    return redirect(url_for("home"))


@app.route("/qr")
def make_qr():
    public_url = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")

    if not public_url:
        return (
            "QR తయారు చేయడానికి ముందుగా PUBLIC_URL సెట్ చేయాలి. "
            "ముందుగా website ను public hosting లో publish చేయండి.",
            400
        )

    if not public_url.startswith("https://"):
        return "PUBLIC_URL తప్పనిసరిగా HTTPS లింక్ అయి ఉండాలి.", 400

    try:
        import qrcode

        qr_image = qrcode.make(public_url)
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="image/png",
            as_attachment=True,
            download_name="Dussehra_Wishes_QR.png"
        )

    except ImportError:
        return "QR package missing. Run: python -m pip install qrcode[pil]", 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
