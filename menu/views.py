from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.auth import logout

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from khayyam import JalaliDatetime
# Create your views here.

from menu.forms import SoldOutForm
from menu.models import SoldOutStatus
from users.models import mother_food , FoodRawMaterial


@login_required
def show_menu(request):
        
            # mother_foods = mother_food.objects.all()
            # foods = FoodRawMaterial.objects.all()

            # food_names = list(FoodRawMaterial.objects.values_list('name', flat=True))
            pizza_single = FoodRawMaterial.objects.filter(mother__name='پیتزا تکنفره')
            pizza_double = FoodRawMaterial.objects.filter(mother__name='پیتزا دونفره')



            return render(request, 'users/menu.html',{'pizza_single':pizza_single,'pizza_double':pizza_double})




from django.http import JsonResponse
from django.shortcuts import render
from .forms import SoldOutForm
from .models import SoldOutStatus
from .signals import menu_status



def set_sold_out(request):
    if request.method == 'POST':# and request.is_ajax():
        form = SoldOutForm(request.POST)
        if form.is_valid():
            form.save()
            product_id = request.POST.get("product")
            product_id = int(product_id)

            food_name = FoodRawMaterial.objects.filter(id=product_id).first()
            food_name = food_name.name

            # ارسال آپدیت به WebSocket

            menu = {
                'name': food_name
            }

            # Retrieve the updated sold-out status list
            sold_out_items = SoldOutStatus.objects.all()  # Get the product ids of sold-out items
            menu_status.send(sender=None, values = menu)

            # return JsonResponse({'status': 'success', 'sold_out_items': list(sold_out_items)})
            form = SoldOutForm()

            

            return render(request, 'sold_out.html', {'form': form,'sold_out_items':sold_out_items})

    else:
        form = SoldOutForm()
        sold_out_items = SoldOutStatus.objects.all()  # Get the product ids of sold-out items

    return render(request, 'sold_out.html', {'form': form,'sold_out_items':sold_out_items})


