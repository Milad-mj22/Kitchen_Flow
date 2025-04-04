from django.utils import timezone
import re
from django.shortcuts import render
# Create your views here.
# api/views.py
from django.http import JsonResponse
from .signals import message_signal



def home(request):
    return JsonResponse({"message": "Welcome to the API!"})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SMS
import json

@csrf_exempt
def receive_sms(request):
    sender = request.GET.get("sender", "Unknown")
    message = request.GET.get("message", "")

    if message:
        SMS.objects.create(sender=sender, message=message)
        content = {'sender':sender,'message':message}
        print(content)
        message_signal.send(sender=None, values = content)

        return JsonResponse({"status": "success"}, status=201)
    return JsonResponse({"status": "error", "message": "Message is empty"}, status=400)




def sms_page(request):
    return render(request, "sms_show.html")




def get_last_sms(request, count):
    try:
        sms_list = SMS.objects.order_by('-received_at')[:count]
        data = [
            {
                'sender': sms.sender,
                'message': sms.message,
                'received_at': sms.received_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for sms in sms_list
        ]
        return JsonResponse({'messages': data})
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return JsonResponse({'error': 'Error fetching messages'}, status=500)
    


def get_total_deposit(request):
    today = timezone.now().date()
    today_sms = SMS.objects.filter(received_at__date=today)  # Adjust timestamp field
    total_sum = 0

    for sms in today_sms:
        match = re.search(r'واریز([\d,]+)', sms.message)
        if match:
            amount = int(match.group(1).replace(',', ''))
            total_sum += amount

    return JsonResponse({"success": True, "total": total_sum})