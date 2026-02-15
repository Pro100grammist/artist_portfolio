import smtplib

sender_email = "senpyinteractive@gmail.com"
app_password = ""
recipient_email = "senpyinteractive@gmail.com"

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, "Test email via Python!")
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
#
#
# from django.core.mail import send_mail
# send_mail('Тема листа', 'Текст листа', 'senpyinteractive@gmail.com', ['senpyinteractive@gmail.com'])


