from flask import Blueprint, render_template

voice_bp = Blueprint("voice_bp", __name__, template_folder="templates")


@voice_bp.route("/voice-to-text")
def voice_to_text():
    return render_template("voice_to_text.html")
