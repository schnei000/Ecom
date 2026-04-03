"""
Envoi d'emails via SMTP.

Variables d'environnement requises (voir .env.example) :
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
Variables optionnelles :
  SMTP_FROM     — adresse expéditeur (défaut: SMTP_USER)
  FRONTEND_URL  — URL du frontend pour construire les liens (défaut: http://localhost:5173)
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_reset_email(to_email: str, reset_token: str) -> None:
    """
    Envoie un email de réinitialisation de mot de passe.

    Raises:
        EnvironmentError: si les variables SMTP ne sont pas configurées.
        smtplib.SMTPException: si l'envoi échoue côté serveur SMTP.
    """
    smtp_host = os.environ.get('SMTP_HOST', '')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    smtp_from = os.environ.get('SMTP_FROM', smtp_user)
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

    if not all([smtp_host, smtp_user, smtp_password]):
        raise EnvironmentError(
            "SMTP non configuré. Définissez SMTP_HOST, SMTP_USER et SMTP_PASSWORD dans .env."
        )

    reset_link = f"{frontend_url}/reset-password?token={reset_token}"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Réinitialisation de votre mot de passe — BoutikLakay"
    msg['From'] = smtp_from
    msg['To'] = to_email

    text_body = (
        "Bonjour,\n\n"
        "Vous avez demandé la réinitialisation de votre mot de passe BoutikLakay.\n\n"
        f"Cliquez sur le lien suivant (valable 15 minutes) :\n{reset_link}\n\n"
        "Si vous n'avez pas fait cette demande, ignorez cet email.\n\n"
        "— L'équipe BoutikLakay"
    )

    html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
  <h2 style="color:#333;">Réinitialisation de mot de passe</h2>
  <p>Bonjour,</p>
  <p>Vous avez demandé la réinitialisation de votre mot de passe <strong>BoutikLakay</strong>.</p>
  <p>
    <a href="{reset_link}"
       style="display:inline-block;padding:12px 24px;background:#2563eb;color:#fff;
              text-decoration:none;border-radius:6px;font-weight:bold;">
      Réinitialiser mon mot de passe
    </a>
  </p>
  <p style="color:#666;font-size:14px;">Ce lien est valable pendant <strong>15 minutes</strong>.</p>
  <p style="color:#666;font-size:14px;">
    Si vous n'avez pas fait cette demande, ignorez cet email.
  </p>
  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">
  <p style="color:#999;font-size:12px;">— L'équipe BoutikLakay</p>
</body>
</html>"""

    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_from, [to_email], msg.as_string())
