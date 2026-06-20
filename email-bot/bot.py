import imaplib
import email
from email.header import decode_header
import time
import resend
from openai import OpenAI

IMAP_SERVER = "mail.spacemail.com"
EMAIL_USER = "info@charly-tricks.dev"
EMAIL_PASS = "TU_PASSWORD_SPACEMAIL"
RESEND_API_KEY = "TU_API_KEY_RESEND"
DEEPSEEK_API_KEY = "TU_API_KEY_DEEPSEEK"

resend.api_key = RESEND_API_KEY
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

SYSTEM_PROMPT = """Sos el asistente virtual de Charly Tricks, respondés emails desde info@charly-tricks.dev.

Tenés DOS roles:

1. VIÑA SAN MARTÍN (uva en fresco):
- Vendemos uva Moscatel, Red Globe y Sweet Globe directo del viñedo en San Martín, Mendoza
- El comprador viene a la finca, elige y corta los racimos
- NO hacemos entregas a domicilio
- Precio por kg a convenir directamente
- Temporada: febrero y marzo
- Contacto: WhatsApp +54 9 263 484-1144

2. CHARLY TRICKS DEV (servicios tech):
- Desarrollo de webs profesionales
- Bots de WhatsApp y Telegram
- Integración de pagos (Ualá Bis, MercadoPago)
- Apps Android
- Contacto: info@charly-tricks.dev o WhatsApp +54 9 263 484-1144

Respondé siempre en español, amable y profesional.
NO inventes precios. Si la consulta es muy específica decí que Charly se comunica personalmente.
Devolvé SOLO el cuerpo del mensaje, sin firma."""

def decode_str(s):
    if not s:
        return ""
    parts = decode_header(s)
    result = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            result += part.decode(enc or "utf-8", errors="ignore")
        else:
            result += part
    return result

def get_body(msg):
    text = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                text += part.get_payload(decode=True).decode(errors="ignore")
    else:
        text = msg.get_payload(decode=True).decode(errors="ignore")
    return text[:2000]

def extract_name(sender):
    if "<" in sender:
        name = sender.split("<")[0].strip().strip('"')
        return name if name else ""
    return ""

def generate_reply(subject, body, sender):
    prompt = f"Email de: {sender}\nAsunto: {subject}\nMensaje:\n{body}"
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

def build_html(body_text, sender_name):
    nombre = f" {sender_name}" if sender_name else ""
    paragraphs = "".join(
        f'<p style="margin:0 0 16px;color:#1a1a1a;font-size:15px;line-height:1.8;">{line}</p>'
        for line in body_text.strip().split("\n") if line.strip()
    )
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f0f0;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f0f0;padding:30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.12);">

  <!-- LOGO ARRIBA -->
  <tr><td style="background:#ffffff;padding:24px;text-align:center;">
    <img src="https://i.postimg.cc/Cxb66Hxj/6475ed80-6cd5-11f1-8324-1d03b29302ea.webp" alt="Charly Tricks Dev" style="max-width:350px;width:100%;height:auto;display:block;margin:0 auto;">
  </td></tr>

  <!-- LÍNEA DORADA -->
  <tr><td style="background:#FFC700;height:4px;font-size:0;">&nbsp;</td></tr>

  <!-- CUERPO BLANCO -->
  <tr><td style="background:#ffffff;padding:36px 32px;">
    <p style="margin:0 0 20px;color:#1A3A2A;font-size:17px;font-weight:700;">Hola{nombre}! 👋</p>
    {paragraphs}
  </td></tr>

  <!-- LOGO ABAJO -->
  <tr><td style="background:#ffffff;padding:16px 24px;text-align:center;border-top:1px solid #f0f0f0;">
    <img src="https://i.postimg.cc/3rPsSwZF/IMG-20260620-WA0015.jpg" alt="Charly Tricks Dev" style="max-width:280px;width:100%;height:auto;display:block;margin:0 auto;">
  </td></tr>

  <!-- FIRMA VERDE -->
  <tr><td style="background:#0F2419;padding:22px 32px;border-top:3px solid #FFC700;">
    <table cellpadding="0" cellspacing="0">
      <tr>
        <td style="padding-right:14px;vertical-align:middle;">
          <div style="width:44px;height:44px;background:#FFC700;border-radius:50%;text-align:center;line-height:44px;font-size:20px;">⚡</div>
        </td>
        <td style="vertical-align:middle;">
          <p style="margin:0;color:#FFC700;font-size:15px;font-weight:700;">Charly Tricks</p>
          <p style="margin:4px 0 0;font-size:12px;">
            <a href="mailto:info@charly-tricks.dev" style="color:#FFC700;text-decoration:none;">info@charly-tricks.dev</a>
            &nbsp;·&nbsp;
            <a href="https://wa.me/5492634841144" style="color:#25d366;text-decoration:none;">+54 9 263 484-1144</a>
            &nbsp;·&nbsp;
            <a href="https://charly-tricks.dev" style="color:rgba(255,255,255,0.4);text-decoration:none;">charly-tricks.dev</a>
          </p>
        </td>
      </tr>
    </table>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

def send_reply(to, subject, body_text, sender_name):
    html = build_html(body_text, sender_name)
    params = {
        "from": "Charly Tricks <info@charly-tricks.dev>",
        "to": [to],
        "subject": f"Re: {subject}",
        "html": html,
    }
    resend.Emails.send(params)
    print(f"✅ Respuesta enviada a {to}")

def check_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")
    _, messages = mail.search(None, "UNSEEN")
    emails = messages[0].split()
    if not emails:
        print("📭 Sin emails nuevos")
    for num in emails:
        _, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        mail.store(num, "+FLAGS", "\\Seen")
        subject = decode_str(msg.get("Subject", "(sin asunto)"))
        sender = msg.get("From", "")
        sender_name = extract_name(decode_str(sender))
        body = get_body(msg)
        print(f"📧 Mail de {sender}: {subject}")
        reply = generate_reply(subject, body, sender)
        send_reply(sender, subject, reply, sender_name)
    mail.logout()

print("🤖 Bot Resend iniciado — info@charly-tricks.dev")
while True:
    try:
        check_emails()
    except Exception as e:
        print(f"❌ Error: {e}")
    time.sleep(120)
