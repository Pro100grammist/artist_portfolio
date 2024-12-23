from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render


from django.core.mail import send_mail
from django.shortcuts import render, redirect


def contact_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', 'Новий запит з контактної форми')
        message = request.POST.get('message', '')
        client_email = request.POST.get('email', '')  # Пошта клієнта, що заповнив форму

        try:
            send_mail(
                subject,  # Тема листа
                f"Повідомлення від {client_email}:\n{message}",  # Текст листа з поштою клієнта
                'senpyinteractive@gmail.com',  # sender_email = EMAIL_HOST_USER (ваша пошта)
                ['senpyinteractive@gmail.com'],  # recipient_email (ваша пошта для отримання повідомлень)
                fail_silently=False,
            )
            return redirect('contact_success')  # Переадресація на сторінку успіху
        except Exception as e:
            return render(request, 'contact_success.html', {'error_message': f"Error: {e}"})
    return render(request, 'contact.html')


def contact_success(request):
    # Відображення сторінки успіху
    return render(request, 'contact_success.html')


def home(request):
    return render(request, "core/home.html")

# def contact_view(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         email = request.POST.get("email")
#         message = request.POST.get("message")
#         send_mail(
#             f"Message from {name}",
#             message,
#             email,
#             ["senpy.interactive@ukr.net"],  # mailbox
#         )
#         messages.success(request, "Your message has been successfully sent!")
#         return redirect("home")
