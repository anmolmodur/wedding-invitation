"""
Wedding invitation helpers.

  encode_guest_token(name)  → base64url token embedded in invite links
  make_invite_url(base, name) → full personalized URL
  build_email_html(...)     → Gmail-safe email with one button (no images)
  build_invite_html(...)    → standalone animated HTML (used for dry-run previews)
"""

import base64
from pathlib import Path


# ── URL helpers ────────────────────────────────────────────────────────────────

def encode_guest_token(name: str) -> str:
    """base64url-encode the guest name, no padding — looks like gibberish in URLs."""
    return base64.urlsafe_b64encode(name.encode("utf-8")).decode("ascii").rstrip("=")


def make_invite_url(page_url: str, guest_name: str) -> str:
    return f"{page_url}?g={encode_guest_token(guest_name)}"


# ── Email HTML (Gmail-safe, inline styles, no JS) ──────────────────────────────

def build_email_html(guest_name: str, invite_url: str, sender_name: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f5f0e8;font-family:Georgia,'Times New Roman',serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"
       style="background-color:#f5f0e8;">
  <tr>
    <td align="center" style="padding:40px 20px;">

      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="max-width:520px;background-color:#fff8f0;border-radius:8px;
                    box-shadow:0 4px 24px rgba(0,0,0,0.12);">
        <tr>
          <td style="padding:56px 48px 48px;text-align:center;">

            <p style="margin:0 0 24px;font-size:12px;letter-spacing:0.15em;
                      text-transform:uppercase;color:#9e8070;">
              You are cordially invited
            </p>

            <h1 style="margin:0 0 16px;font-size:26px;color:#4a3728;font-weight:normal;">
              Dear {guest_name},
            </h1>

            <p style="margin:0 0 36px;font-size:15px;color:#6b4f3a;line-height:1.7;">
              We have something special waiting for you.<br>
              Click below to open your personal invitation.
            </p>

            <a href="{invite_url}"
               style="display:inline-block;padding:16px 52px;background-color:#922b21;
                      color:#ffffff;text-decoration:none;border-radius:50px;
                      font-size:13px;letter-spacing:0.15em;text-transform:uppercase;
                      font-family:Georgia,'Times New Roman',serif;">
              Open Your Invitation &#10084;
            </a>

            <p style="margin:36px 0 0;font-size:12px;color:#b09880;letter-spacing:0.06em;">
              &mdash; {sender_name}
            </p>

          </td>
        </tr>
      </table>

      <p style="margin:20px 0 0;font-size:11px;color:#b09880;
                font-family:Georgia,'Times New Roman',serif;">
        If the button does not open, copy this link into your browser:<br>
        <a href="{invite_url}" style="color:#922b21;">{invite_url}</a>
      </p>

    </td>
  </tr>
</table>
</body>
</html>"""


# ── Standalone animated HTML (dry-run previews only) ──────────────────────────

def build_invite_html(
    guest_name: str,
    rsvp_url: str,
    front_image_path: str,
    back_image_path: str,
    sender_name: str,
) -> str:
    """Self-contained animated page with base64-embedded images — for local preview only."""
    front_src = f"data:image/png;base64,{_encode_image(front_image_path)}"
    back_src  = f"data:image/png;base64,{_encode_image(back_image_path)}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wedding Invitation — {guest_name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: linear-gradient(135deg, #f5f0e8 0%, #ede0cc 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Georgia, 'Times New Roman', serif;
    padding: 20px;
  }}

  .container {{
    text-align: center;
    max-width: 600px;
    width: 100%;
  }}

  .greeting {{
    font-size: 1.1em;
    color: #6b4f3a;
    margin-bottom: 28px;
    letter-spacing: 0.05em;
  }}

  .env-stage {{
    position: relative;
    width: 100%;
    max-width: 520px;
    padding-bottom: 65%;
    margin: 0 auto 32px;
    perspective: 1200px;
    cursor: pointer;
    user-select: none;
  }}

  .env-back {{
    position: absolute;
    inset: 0;
    background: #fff8f0;
    border-radius: 4px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.18);
    z-index: 1;
  }}

  .card-section {{
    position: absolute;
    left: 10%;
    right: 10%;
    bottom: 5%;
    z-index: 2;
    cursor: default;
    opacity: 0;
  }}

  .env-stage.open .card-section {{
    animation: cardReveal 3.2s cubic-bezier(0.4, 0, 0.2, 1) 0s forwards;
  }}

  @keyframes cardReveal {{
    0%    {{ transform: translateY(50%);  opacity: 1; z-index: 5;  clip-path: inset(50% 0 0 0); }}
    25%   {{ transform: translateY(50%);  opacity: 1; z-index: 5;  clip-path: inset(0% 0 0 0); }}
    65%   {{ transform: translateY(-30%); opacity: 1; z-index: 5;  }}
    65.5% {{ transform: translateY(-30%); opacity: 1; z-index: 10; }}
    100%  {{ transform: translateY(35%);  opacity: 1; z-index: 10; }}
  }}

  .card-clip-wrapper {{ perspective: 1200px; }}
  .env-stage.open .card-clip-wrapper {{
    animation: clipReveal 3.2s cubic-bezier(0.4, 0, 0.2, 1) 0s forwards;
  }}
  @keyframes clipReveal {{
    0%   {{ clip-path: inset(0 0 70% 0); }}
    28%  {{ clip-path: inset(0 0 70% 0); }}
    57%  {{ clip-path: inset(0 0 0%  0); }}
    100% {{ clip-path: none; }}
  }}

  .card-flipper {{
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
  }}
  .card-flipper.flipped {{ transform: rotateY(180deg); }}

  .card-front,
  .card-back {{
    backface-visibility: hidden;
    border-radius: 6px;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0,0,0,0.25);
  }}

  .card-front img {{ width: 100%; height: auto; display: block; }}

  .card-back {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    transform: rotateY(180deg);
  }}
  .card-back img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}

  .env-pocket {{
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 100%;
    background: #fff8f0;
    z-index: 6;
    clip-path: polygon(0% 0%, 0% 100%, 100% 100%, 100% 0%, 50% 47%, 0% 0%);
  }}
  .env-pocket::before,
  .env-pocket::after {{
    content: '';
    position: absolute;
    bottom: 0;
    width: 0; height: 0;
    border-style: solid;
  }}
  .env-pocket::before {{
    left: 0;
    border-width: 0 0 160px 200px;
    border-color: transparent transparent #e8d8c4 transparent;
    opacity: 0.55;
  }}
  .env-pocket::after {{
    right: 0;
    border-width: 160px 0 0 200px;
    border-color: transparent transparent transparent #e8d8c4;
    opacity: 0.55;
  }}

  .env-flap {{
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 55%;
    transform-origin: top center;
    transform-style: preserve-3d;
    transition: transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 4;
  }}
  .env-flap-inner {{
    position: absolute;
    inset: 0;
    background: #f5e6d3;
    clip-path: polygon(0 0, 100% 0, 50% 85%);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    backface-visibility: hidden;
  }}

  .seal {{
    position: absolute;
    top: 47%;
    left: 50%;
    transform: translateX(-50%);
    width: 48px; height: 48px;
    background: radial-gradient(circle at 40% 35%, #c0392b, #922b21);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.3);
    z-index: 7;
    transition: opacity 0.3s ease, transform 0.3s ease;
  }}

  .env-stage.open .env-flap {{ transform: rotateX(-175deg); }}
  .env-stage.open .seal {{
    opacity: 0;
    transform: translateX(-50%) scale(0.5);
    pointer-events: none;
  }}

  .hint {{
    font-size: 0.82em;
    color: #9e8070;
    margin-top: 50px;
    margin-bottom: 30px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    transition: opacity 0.4s;
  }}

  .rsvp-section {{
    margin-top: 20px;
    padding-bottom: 8px;
    opacity: 0;
    transition: opacity 0.6s ease;
    pointer-events: none;
  }}
  .rsvp-section.visible {{ opacity: 1; pointer-events: auto; }}

  .rsvp-btn {{
    display: inline-block;
    padding: 14px 44px;
    background: linear-gradient(135deg, #c0392b, #922b21);
    color: #fff !important;
    text-decoration: none;
    border-radius: 50px;
    font-size: 1em;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    box-shadow: 0 4px 18px rgba(192,57,43,0.35);
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .rsvp-btn:hover {{
    transform: translateY(-2px);
    box-shadow: 0 7px 24px rgba(192,57,43,0.45);
  }}

  .footer {{
    margin-top: 24px;
    font-size: 0.8em;
    color: #b09880;
    letter-spacing: 0.06em;
  }}
</style>
</head>
<body>
<div class="container">
  <p class="greeting">Dear {guest_name},<br>you are warmly invited to celebrate with us.</p>

  <p class="hint">Click the envelope to open your invitation</p>

  <div class="env-stage" id="envelopeStage">
    <div class="env-back"></div>

    <div class="card-section" id="cardSection">
      <div class="card-clip-wrapper">
        <div class="card-flipper" id="cardFlipper">
          <div class="card-front">
            <img src="{front_src}" alt="Invitation front">
          </div>
          <div class="card-back">
            <img src="{back_src}" alt="Invitation back">
          </div>
        </div>
      </div>
      <p class="hint" id="flipHint" style="opacity:0;">Click the card to see the back</p>
      <div class="rsvp-section" id="rsvpSection">
        <a href="{rsvp_url}" class="rsvp-btn" target="_blank">RSVP Now</a>
        <p class="footer">&mdash; {sender_name}</p>
      </div>
    </div>

    <div class="env-pocket"></div>

    <div class="env-flap">
      <div class="env-flap-inner"></div>
    </div>
    <div class="seal">&#10084;</div>
  </div>
</div>

<script>
(function () {{
  const stage    = document.getElementById('envelopeStage');
  const cardSec  = document.getElementById('cardSection');
  const flipper  = document.getElementById('cardFlipper');
  const flipHint = document.getElementById('flipHint');
  const rsvpSec  = document.getElementById('rsvpSection');
  let opened = false, flipped = false;

  stage.addEventListener('click', function () {{
    if (opened) return;
    opened = true;
    stage.classList.add('open');
    setTimeout(function () {{
      flipHint.style.opacity = '1';
      rsvpSec.classList.add('visible');
    }}, 4200);
  }});

  cardSec.addEventListener('click', function (e) {{
    if (!opened) return;
    e.stopPropagation();
    flipped = !flipped;
    flipper.classList.toggle('flipped', flipped);
  }});
}})();
</script>
</body>
</html>"""


def _encode_image(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("ascii")
