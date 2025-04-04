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
    now = timezone.now()
    # 🟢 مقدار ساعت را برای دیباگ به‌صورت دستی تغییر دهید


    # Determine the start of the custom day (2:00 AM today)
    if now.hour < 2:
        start_time = (now - timezone.timedelta(days=1)).replace(hour=2, minute=0, second=0, microsecond=0)
    else:
        start_time = now.replace(hour=2, minute=0, second=0, microsecond=0)
    
    # End time is 24 hours after the start time
    end_time = start_time + timezone.timedelta(days=1)

    # Filter SMS records in the range from 2 AM today to 2 AM the next day
    today_sms = SMS.objects.filter(received_at__gte=start_time, received_at__lt=end_time)

    total_sum = 0
    for sms in today_sms:
        match = re.search(r'واریز([\d,]+)', sms.message)
        if match:
            amount = int(match.group(1).replace(',', ''))
            total_sum += amount

    return JsonResponse({"success": True, "total": total_sum})