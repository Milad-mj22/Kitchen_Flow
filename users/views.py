from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.auth import logout

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from khayyam import JalaliDatetime

from order_flow.models import MaterialUsage, OrderStep
from users.EntryModule.EntryUtils import get_latest_exit, is_user_in , UserWorkTimeManager
from users.utils.CalulatedDistance import calculate_distance

from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from django.views import generic
from .models import AllowedLocation, CapturedImage, Inventory, InventoryLog, MaterialComposition, Post,Tools,full_post,Profile
from django.shortcuts import get_object_or_404
import numpy as np
from django.http import HttpResponse
from .forms import PostForm_add_material,PostFormAddMotherMaterial,PostFormAddRestaurant,EntryExitForm
from .models import User,jobs , Projects , raw_material,SnappFoodList
from .models import Profile as model_profile
from .models import create_order as ModelCreateOrder
from .models import mother_material as MotherMaterial
from .models import raw_material as RawMaterial
from .models import FoodRawMaterial 
from .models import Warehouse
from .models import mother_food as MotherFood
from .models import EntryExitLog

from django.views.decorators.csrf import csrf_protect
import os
from datetime import datetime, timezone
import jdatetime
from snapp_discount.getPrice import get_price
from .constants import translate
import json
from decimal import Decimal
from users import models
from django.http import JsonResponse

from django.db.models import Sum, Prefetch, F, DecimalField, Q  # Import DecimalField
from django.db.models.functions import Coalesce
import time
from persiantools.jdatetime import JalaliDate


import base64
from django.core.files.base import ContentFile

from .models import RestaurantBranch,NightOrderRemainder

CACHE_CITIES = 'snapp_discount/cache/cities'

# backend_endpoint

BACKEND_ENDPOINT = 'http://127.0.0.1:8000' 

from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        print('milad'*20)
        messages.success(request, "You have been logged out successfully.")
        return redirect(to='login')
        return redirect('users-register')
        return self.post(request, *args, **kwargs)


def home(request):
    return render(request, 'users/home.html')


class RegisterView(View):
    a = jobs.objects.all()
    print(a)
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            # form.save()


            obj =form.save()
            
            form.save()

            b =model_profile.objects.all().last()
            b.job_position_id =int(request.POST['job_position'])
            b.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True

        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)



class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


@login_required
def profile(request):
        if request.method == 'POST':
            user_form = UpdateUserForm(request.POST, instance=request.user)
            profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile is updated successfully')
                return redirect(to='users-profile')
        else:
            user_form = UpdateUserForm(instance=request.user)
            # if request.user
            try:

                user = Profile.objects.get(id = request.user.id)

                # profile_form = {'first_name':None,'last_name':None,'job_persian_name':None,'job_short_name':None,'job_describe':None}
                # first_name = user.first_name
                # last_name = user.last_name
                # user_name = user.user
                # job_persian_name =  user.job_position.persian_name
                # job_short_name =  user.job_position.short_name
                # job_describe =  user.job_position.describe

                # profile_form = {'first_name':first_name,'last_name':last_name,'job_persian_name':job_persian_name,'job_short_name':job_short_name,'job_describe':job_describe}




            except Exception as e:
                print('Error profile_form :' , e)
                return render(request, 'users/profile.html', {'user_form': user_form})


        return render(request, 'users/profile.html', {'user_form': user_form, 'user': user})


# @login_required
def tools(request):
    queryset = Tools.objects.all().order_by('-title').reverse()
    print('queryset',queryset)
    print('show tools page')
    
    return render(request, 'users/tools_new.html',{'tools':queryset})


@login_required
def create_order(request):

    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')


        for field,value in data.items():
            if value.isnumeric():
                data[field]=float(value)



        b = ModelCreateOrder.objects.update_or_create(author = request.user , content = data)


        # if form.is_valid():
            # obj =form.save(commit=False)
            # obj.author = User.objects.get(pk=request.user.id)
            # form.save()
        messages.success(request,'New Forum Successfully Added')
        return redirect('/profile/my_orders')

    
        # else:
        #     messages.error(request, 'Please correct the following errors:')
        #     materials = raw_material.objects.all()
        #     return render(request, 'users/post_list_quil.html', {'materials': materials})



    else:

        # materials = raw_material.objects.all().order_by('-mother_id')
        # return render(request, 'users/create_order.html', {'materials': materials})





        mother_materials = MotherMaterial.objects.prefetch_related('mother_material').order_by('describe').all()
 
        return render(request, 'users/create_order.html', {'mother_materials': mother_materials})
    














@login_required
def my_orders(request):
    from datetime import datetime
    orders = ModelCreateOrder.objects.order_by('updated_at')
    # orders = orders.order_by('-updated_at').reverse()
    orders = orders.reverse()
    orders = orders[:15]
    editable = []

    
    materials_quantity = get_material_quantity(show_all=True)


    for order in orders:
        order.content = eval(order.content)
        try:
            if order.night_order is not None:
                order.night_order = eval(order.night_order)

        except:
            print('Error : my_orders night order ERORrrrrrrrrrrr')

        diff =  datetime.now() - order.created_at 
        sec = diff.total_seconds()  
        
        if sec < 28800:
            order.created_at = True
        else:
            order.created_at = False
            # editable.append(False)



        date = order.updated_at
        # convert_to_jalali(date_str=date)
        jalali_datetime = jdatetime.date.fromgregorian(date=date)
        # Format the Jalali date and time
        formatted_jalali_date = jalali_datetime.strftime('%Y-%m-%d')  # Format the Jalali date
        formatted_jalali_time = date.strftime('%H:%M')  # Format the time (remains the same)

        # Combine date and time
        formatted_jalali_datetime = f"{formatted_jalali_date} {formatted_jalali_time}"
        order.updated_at = formatted_jalali_datetime








            # material = materials_quantity.get(name = rw)

      
            # quantity =float(Decimal(material.total_quantity))

            # if quantity<value:

            #     if rw in list(required_items.keys()): 

            #         required_items[rw] =round(value - quantity + required_items[rw],3)
            #     else:
            #         required_items[rw] =round(value - quantity,3)






        values = order.content

        data = {}



        for field in values.keys():
            if field!='additional_details'  :
                try:
                    if float(values[field])>0:
                        # try:
                            # print(field)
                            value = values[field]

                            data = {}

                            obj = raw_material.objects.filter(name = field).first()
                            if obj.unit != 'number':
                                values[field] = '{} {}'.format(round(values[field],3),translate(obj.unit))
                            else:
                                values[field] = '{} {}'.format(int(values[field]),translate(obj.unit))


                     

                            material = materials_quantity.get(name = field)
                            quantity =float(Decimal(material.total_quantity))
                            
                            exist=True
                            if quantity<round(value,3):
                                exist = False


                            values[field] += '| موجود {}'.format(quantity)

                            if quantity!=0:
                                values[field] +=' {}'.format( translate(obj.unit))


                        
                            data = {
                                'amount':values[field],
                                'exist' : exist
                            }

                            values[field] = data
                        
                        
                        # except:
                        #     print('eror')
                except:
                    print(values[field])


    return render(request, 'users/my_orders.html', {'orders': orders,'editable':editable})




def convert_to_jalali(date_str):
    # Parse the date string to a datetime object
    date_obj = datetime.strptime(date_str, '%b. %d, %Y, %I:%M %p')
    
    # Convert to Jalali
    jalali_date = jdatetime.date.fromgregorian(date=date_obj)

    # Format the Jalali date
    return jalali_date.strftime('%Y-%m-%d')


@login_required
def add_raw_material(request):

    if request.method == 'POST':
        form = PostForm_add_material(request.POST)
        if form.is_valid():
            obj =form.save(commit=False)
            obj.author = User.objects.get(pk=request.user.id)
            mother_id = form.cleaned_data['mother_material']
            obj.mother = get_object_or_404(MotherMaterial, id=mother_id)
            form.save()
            messages.success(request,'New Forum Successfully Added')
            return redirect('/profile/my_orders')

        
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request,'users/create_material.html',{'form':form})
        
    else:
        form = PostForm_add_material()
        context = {
            'form':form
        }
        return render(request, 'users/create_material.html',context)




@login_required
def add_mother_material(request):

    if request.method == 'POST':
        form = PostFormAddMotherMaterial(request.POST)
        if form.is_valid():
            obj =form.save(commit=False)
            obj.author = User.objects.get(pk=request.user.id)
            form.save()
            messages.success(request,'New Forum Successfully Added')
            return redirect('/profile/my_orders')

        
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request,'users/create_mother_material.html',{'form':form})
        
    else:
        form = PostFormAddMotherMaterial()
        context = {
            'form':form
        }
        return render(request, 'users/create_mother_material.html',context)








@login_required
def post_edit_quil(request,id):
    materials = get_object_or_404(ModelCreateOrder,id=id)
    materials = eval(materials.content)


    if 'additional_details' in materials.keys():
        details = materials['additional_details']
        materials.pop('additional_details')
    else:
        details=''


    if request.method == 'GET':

        # new_mat = {}
        # for field,value in materials.items():
        #     if isinstance(value,int) :
        #         new_mat[field] = value

        # context = {'form': PostForm_tinymce(instance=post), 'id': id}
        # return render(request,'users/create_post.html',context)
        # materials = raw_material.objects.all()
        return render(request, 'users/edit_order.html', {'materials': materials,'edit':True,'details':details})


   
    elif request.method == 'POST':

        data = dict(request.POST.dict())

        data.pop('csrfmiddlewaretoken','Not found')


        for field,value in data.items():
            if value.isnumeric():
                data[field]=float(value)


        ret = ModelCreateOrder.objects.filter(id=id).first()
        if ret:
            ret.content=data
            ret.save()


        # b = ModelCreateOrder.objects.update_or_create(author = request.user , content = data)


        messages.success(request, 'The post has been updated successfully.')
        return redirect('/profile/my_orders')
        # else:
        #     messages.error(request, 'Please correct the following errors:')
        #     return render(request,'posts/post_form.html',{'form':form})
        





# @login_required
def show_order(request,id):
    materials = get_object_or_404(ModelCreateOrder,id=id)
    materials = eval(materials.content)
    if request.method == 'GET':

        # context = {'form': PostForm_tinymce(instance=post), 'id': id}
        # return render(request,'users/create_post.html',context)
        # materials = raw_material.objects.all()






        return render(request, 'users/edit_order.html', {'materials': materials,'edit':False})


   
    elif request.method == 'POST':

        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')


        b = ModelCreateOrder.objects.update_or_create(author = request.user , content = data)


        messages.success(request, 'The post has been updated successfully.')
        return redirect('/profile/my_orders')
        # else:
        #     messages.error(request, 'Please correct the following errors:')
        #     return render(request,'posts/post_form.html',{'form':form})
        



@login_required
def snapp(request):

    print('show snapp page')

    try:
        cities = os.listdir(CACHE_CITIES)
    except:
        cities = []

    return render(request, 'users/snapp_cities.html',{'cities':cities})




def show_restaurant_list(request,city):


    print('show snapp page')
    restaurants = SnappFoodList.objects.all().order_by('-name')

    try:
        path = os.path.join(CACHE_CITIES,city)
        restaurants_ = os.listdir( path)

        restaurants = []

        for res in restaurants_:
            restaurants.append(res[:-5])

    except:
        restaurants = []

    return render(request, 'users/snapp_restaurants.html',{'city':city,'restaurants':restaurants})







def restaurant_food_list(request,city,res_name):


    # try:

    gp = get_price(res_name=res_name,city=city)




    prices = gp.ret_price()
    prices = prices[res_name]
    print('show restaurant_list page')


    # except:
    #     prices = []


    return render(request, 'users/show_prices.html',{'city':city,'prices':prices})


def add_restaurant(request):


    if request.method == 'POST':
        form = PostFormAddRestaurant(request.POST)
        if form.is_valid():
            obj =form.save(commit=False)
            obj.author = User.objects.get(pk=request.user.id)
            form.save()

            # get_price()

            data = request.POST.dict()

            gp = get_price(res_name=data['name'],res_link=data['link'],city= data['city'])
            gp.get_name_price()

            messages.success(request,'New Forum Successfully Added')

            # return render(request, 'users/snapp_restaurants.html',{'city':city,'restaurants':restaurants})
            return tools(request=request)
        else:
            messages.error(request, 'Please correct the following errors:')
            return render(request,'users/create_mother_material.html',{'form':form})
        
    else:
        form = PostFormAddRestaurant()
        context = {
            'form':form
        }
        return render(request, 'users/create_mother_material.html',context)






@login_required
def print_order(request,id):
    materials = get_object_or_404(ModelCreateOrder,id=id)
    
    material_dict = eval(materials.content)
    new_materials ={}

    orderStep1 = OrderStep.objects.filter(order=materials,step_number=1).first()
    orderStep2 = OrderStep.objects.filter(order=materials,step_number=2).first()
    orderStep3 = OrderStep.objects.filter(order=materials,step_number=3).first()
    orderStep4 = OrderStep.objects.filter(order=materials,step_number=4).first()



    for material,value in material_dict.items():
        try:
           if value!='':
                if float(value)>0:
                    unit =''
                    try:
                        ret = raw_material.objects.get(name=material)
                        unit = ret.unit
                        mother_id = ret.mother.describe
                        material_id = ret.describe
                        full_id = mother_id+material_id

                    except:
                        print('Cant get unit {}'.format(material))
                    new_materials[material] = {}
                    new_materials[material]['code'] = str(full_id)
                    new_materials[material]['unit'] = translate(str(unit))
                    
                    new_materials[material]['value'] = str(value)

                    if orderStep2:
                        step2 = MaterialUsage.objects.filter(step=orderStep2,material=ret).first()
                        new_materials[material]['step2'] = str(step2.quantity)
                    if orderStep3:
                        step3 = MaterialUsage.objects.filter(step=orderStep3,material=ret).first()
                        new_materials[material]['step3'] = str(step3.quantity)
                    if orderStep4:
                        step4 = MaterialUsage.objects.filter(step=orderStep4,material=ret).first()
                        new_materials[material]['step4'] = str(step4.quantity)
        except Exception as e:
            print(e)


    headers = ['کد کالا','نام کالا','واحد','درخواستی','ارسالی','تحویلی','مانده','کد کالا','نام کالا','واحد','درخواستی','ارسالی','تحویلی','مانده']

    return render(request, 'users/print_order.html', {'materials': new_materials,'edit':False,'headers':headers})

        



@login_required
def foodRawMaterials(request):

    print('show snapp page')
    restaurants = FoodRawMaterial.objects.all().order_by('-name')


    return render(request, 'users/food_raw_materials.html',{'foods':restaurants})






def addfoodrawmaterial(request):

    if request.method == 'POST':
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')
        food_name = data['food_name']
        data.pop('food_name','Not found location')

        mother_food =int(data['mother_food'])
        data.pop('mother_food','mother_food')



        if  FoodRawMaterial.objects.filter(name=food_name).first()==None:


            user = User.objects.get(pk=request.user.id)
    
            values ={}

            for field,value in data.items():
                # try:
                    if float(value)>0:
                        values[field]=value
                        # item = raw_material.objects.filter(name=field).first()
                        # item_id = item.id
                        # item = raw_material.objects.get(id=item_id)
                        # b=AddtoStore.objects.create(item=item,location=location,count =value, author = user)
                        # update_store(item=item,location=location,value=value)
                        # print(b)
                # except:
                # print('error in add to store')

            obj_mother_food = MotherFood.objects.filter(id=mother_food).first()
            if obj_mother_food:
                food_name = obj_mother_food.name+' '+food_name

            b = FoodRawMaterial.objects.update_or_create(name= food_name, data = values, mother =obj_mother_food )
            messages.success(request,'New Item Successfully Added')

            return redirect('/tools/foodrawmaterials')
        
        else:
            print('mojooooooodddddd')
            return redirect('/tools/foodrawmaterials')



    else:
        mother_materials = MotherMaterial.objects.prefetch_related('mother_material').all()
        mother_foods = MotherFood.objects.all()

        foods = FoodRawMaterial.objects.all()
        food_list =[]
        for food in foods:
            food_list.append(food.name)
        return render(request, 'users/create_food_raw_material.html', {'mother_materials': mother_materials,'food_names':food_list,'mother_foods':mother_foods})
    



def add_count_to_materials(mother_materials,data):

    # mother_materials = MotherMaterial.objects.all()

    # Create a dictionary to store submaterials for each mother material
    materials_with_submaterials = {}

    

    # Iterate through each mother material and fetch related submaterials
    for mother_material in mother_materials:
        submaterials = mother_material.mother_material.all()
        for submaterial in submaterials :
            # count = fullStore.objects.filter(item = submaterial.id).all()
            if submaterial.name in data:
                submaterial.count = data[submaterial.name]
        materials_with_submaterials[mother_material] = submaterials

    return materials_with_submaterials



def show_food_material(request,id):
        
    if request.method == 'POST':
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')
        food_name = data['food_name']

        



        data.pop('food_name','Not found location')
        user = User.objects.get(pk=request.user.id)

        values ={}

        for field,value in data.items():
            try:
                if value !='':
                    if float(value)>0:
                        values[field]=value
            except:
                print('error in add to store')

        
        food = FoodRawMaterial.objects.filter(name=food_name).first()
        food.data=values
        food.save()
        # _,ret = FoodRawMaterial.objects.update(name= food_name, data = values)
        # if ret:
        #     messages.success(request,'New Item Successfully Added')

        return redirect('/tools/foodrawmaterials')
        # else:
        #     print('Error in update data')
        #     return redirect('/tools/foodrawmaterials')

  
    else:



        mother_materials = MotherMaterial.objects.prefetch_related(
            Prefetch(
                'mother_material',  # Replace 'raw_material' with the correct related_name of RawMaterial in MotherMaterial
                queryset=RawMaterial.objects.order_by('describe')  # Sorting by 'describe' in ascending order
            )
        ).order_by('describe')


        for mother_material in mother_materials:
            submaterials = mother_material.mother_material.all()
            for submaterial in submaterials :
                print(submaterial)



    

        # foods = FoodRawMaterial.objects.all()
        food_name = FoodRawMaterial.objects.filter(id=id).first()
        if food_name.data is not None:
            mother_materials = add_count_to_materials(mother_materials,food_name.data)
        return render(request, 'users/show_food_raw_material.html', {'mother_materials': mother_materials,'food_name':food_name})
    




@login_required
def night_food_order(request):
    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')

        materials_quantity = get_material_quantity(show_all=True)

        raw_material={}
        required_items = {}

        for food_name,value in data.items():
            # if value.isnumeric():
                data[food_name]=float(value)
                
                ret = FoodRawMaterial.objects.filter(name=food_name).first()

                if ret :
                    for material in ret.data.keys():
                        
                        
                        new_value = round(float(ret.data[material])*float(value),4)


                        if material in raw_material.keys():

                            raw_material[material]+=new_value
                        
                        else:
                            raw_material[material]=new_value




        for rw , value in raw_material.items():

            material = materials_quantity.get(name = rw)

      
            quantity =float(Decimal(material.total_quantity))

            if quantity<value:

                if rw in list(required_items.keys()): 

                    required_items[rw] =round(value - quantity + required_items[rw],3)
                else:
                    required_items[rw] =round(value - quantity,3)


        ret , status = ModelCreateOrder.objects.update_or_create(author = request.user , content = raw_material, night_order = data )

        if status:
            messages.success(request,'New Forum Successfully Added')

        if required_items=={}:
            return redirect('/profile/my_orders')
        else:
            return render(request, 'users/reqiured_items.html', {'required_items': required_items})



    else:
        mother_foods = MotherFood.objects.prefetch_related('mother_food_id').all()
        # mother_foods = MotherFood.objects.all()

        # foods = FoodRawMaterial.objects.all()
        # food_list =[]
        # for food in foods:
        #     food_list.append(food.name)
        producible_foods = calculateProducibleMeals()




        for mother_food in mother_foods:
            total = 0
            for food in mother_food.mother_food_id.all():
                food_name = food.name

                if food_name in list(producible_foods.keys()):
                    food.producible_quantity = producible_foods[food_name]
                    total += producible_foods[food_name]  
                else:
                    food.producible_quantity = 0


            mother_food.producible_quantity = total                 


        return render(request, 'users/night_order.html', {'mother_foods': mother_foods})
    




def show_night_order_material(request):



        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')

        materials_quantity = get_material_quantity(show_all=True)

        raw_material={}
        required_items = {}
        foods = {}

        for food_name,value in data.items():
            # if value.isnumeric():
                print(float(value))
                if float(value)>0:
                    data[food_name]=float(value)
                    
                    ret = FoodRawMaterial.objects.filter(name=food_name).first()

                    if ret :

                        foods[food_name] = {
                            'value': value,
                        }
                        for material in ret.data.keys():
                            
                            
                            new_value = round(float(ret.data[material])*float(value),4)


                            if material in raw_material.keys():

                                raw_material[material]+=new_value
                                # raw_material[material] = round(raw_material[material],4)
                            
                            else:
                                raw_material[material]=new_value
                                # raw_material[material] = round(raw_material[material],4)



        items = {}


        for rw , value in raw_material.items():

            material = materials_quantity.get(name = rw)
            if material:
        
                quantity =float(Decimal(material.total_quantity))
                quantity = round(quantity,4)
                value = round(value,4)
                items[rw] = {
                    'required': value,
                    'available': quantity,
                    'exist': quantity >= value
                }




        return render(request, 'users/show_night_order_material.html', {'items': items , 'foods':foods})











def calculateProducibleMeals():

    # mother_materials = MotherFood.objects.prefetch_related('mother_food_id').all()
    producible_foods = {}

    materials = get_material_quantity()  # Get available materials with quantities
    exist_materials = materials.values_list('name', flat=True)  # Get the names of existing materials

    foods = FoodRawMaterial.objects.all()  # Get all food recipes

    for food in foods:
        recepi = food.data  # Recipe for the food (ingredients and their required quantities)
        print('Food:', food.name)
        
        max_food_quantity = float('inf')  # Start with infinity, then find the limiting material

        for item, required_qty in recepi.items():  # Iterate through each material in the recipe
            if item not in exist_materials:  # If the material is not available, you can't make this food
                max_food_quantity = 0
                break

            material = materials.get(name=item)  # Get the available material from the materials list

            # Calculate how many times the available material can meet the required quantity
            available_qty = Decimal(material.total_quantity)
            possible_quantity = available_qty // Decimal(required_qty)  # Use floor division

            # The maximum food quantity is determined by the most limiting ingredient
            max_food_quantity = min(max_food_quantity, possible_quantity)

        # if max_food_quantity==0:
        #     break


        if max_food_quantity > 0 and  max_food_quantity != float('inf'):  # If at least 1 of this food can be made
            # producible_foods.append((food, max_food_quantity))  # Append the food and the quantity
            producible_foods[food.name] = int(max_food_quantity)
    # Print the producible foods and the quantity
    # for food, quantity in producible_foods:
    #     print(f'You can make {quantity} of {food.name}')
    print(producible_foods)

    return producible_foods







def load_temp(request):
    return render(request,'users/temp.html')





@login_required
def add_store(request):

    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')



        if 'warehouse' in data.keys():
            ware_house = data['warehouse']
            data.pop('warehouse','Not found')

        else:
            return
        
        
        if 'receipt_number' in data.keys():
            receipt_number = data['receipt_number']
            data.pop('receipt_number','Not found')

        else:
            return
        

        image_data = request.POST.get('captured_image')
        # print('image_data',image_data)
        if image_data:
            data.pop('captured_image','Not found')
            try:


                format, imgstr = image_data.split(';base64,') 
                ext = format.split('/')[-1]  

                # Fix padding issue
                missing_padding = len(imgstr) % 4  
                if missing_padding:  
                    imgstr += '=' * (4 - missing_padding)  # Add missing padding  


                # image = ContentFile(base64.b64decode(imgstr), name=f"receipt_image.{ext}")
                # print('3')

                
                print(f'Format: {format}')  # Check the extracted format
                print(f'Ext: {format.split("/")[-1]}')  # Check extension
                print(f'First 50 chars of imgstr: {imgstr[:50]}')  # Check base64 content

                try:
                    # image = ContentFile(base64.b64decode(imgstr), name=f"receipt_image.{ext}")
                    image = ContentFile(base64.urlsafe_b64decode(imgstr), name=f"receipt_image.{ext}")
                    print("Image successfully created")
                except Exception as e:
                    print(f"Error: {e}")
            
                saved_image = CapturedImage.objects.create(image=image,receipt_number=receipt_number)  # Save to model
                print('saved_image : ',saved_image)
            except:
                print('Error in save image')
                pass
                
            
        print('milaaaaaaaad')



        profile = Profile.objects.get(id = request.user.id)

        ware_house = Warehouse.objects.get(id = ware_house)

        values ={}

        for field,value in data.items():
            try:
                if value !='':
                    if float(value)>0:
                        values[field]=value
                        decimal_value = Decimal(value)
                        raw_material_instance = raw_material.objects.get(name=field)
                        inventory, created = Inventory.objects.get_or_create(inventory_raw_material=raw_material_instance,warehouse=ware_house)
                        inventory.add_stock(amount=decimal_value,user=profile,receipt_number=receipt_number)



            except:
                print('error in add to store')
                messages.success(request,'بروز خطا در هنگام اضافه نمودن')
                return redirect('/')  # Redirect to your desired page

        messages.success(request,'مقادیر مورد نظر با موفقیت اضافه گردید')
        # return redirect('/profile/my_orders')
        return redirect('success_page')  # Redirect to your desired page

    else:

        mother_materials = MotherMaterial.objects.prefetch_related('mother_material').order_by('describe').all()

        ware_houses = Warehouse.objects.all()
 
        return render(request, 'users/store_add.html', {'mother_materials': mother_materials,'warehouses':ware_houses})
    



from .forms import MaterialCompositionForm

def material_composition_view(request):
    if request.method == 'POST':
        form = MaterialCompositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Redirect to a success page
    else:
        form = MaterialCompositionForm()
    
    return render(request, 'material_composition.html', {'form': form})




def get_total_quantity(material):
    total = Inventory.objects.filter(inventory_raw_material=material).aggregate(Sum('quantity'))['quantity__sum']
    return total or 0  # اگر مقدار None بود، 0 برگردانید







# views.py
def material_composition_view(request):



    if request.method == 'POST':

        main_materials = MaterialComposition.objects.values_list("main_material__name", flat=True).distinct()



        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')



        if 'warehouse' in data.keys():
            ware_house = data['warehouse']
            data.pop('warehouse','Not found')

        else:
            return


        profile = Profile.objects.get(id = request.user.id)
        ware_house = Warehouse.objects.get(id = ware_house)




        
        for key , value in data.items():
            discard=False
            if float(value)>0:

                if key not in main_materials:

                    print('Remove :',key , 'value : ',value)
                    decimal_value = Decimal(value)
                    raw_material_instance = raw_material.objects.get(name=key)
                    inventory, created = Inventory.objects.get_or_create(inventory_raw_material=raw_material_instance,warehouse=ware_house)
                    status,message = inventory.remove_stock(amount=decimal_value,user=profile)
                    # print(status,message)

                    if not status:
                        return redirect('error_page')
                
                    


                else:


                    print('ADD: ',key , 'value : ',value)
                    receipt_number = '{}'.format(9000)
                    decimal_value = Decimal(value)
                    raw_material_instance = raw_material.objects.get(name=key)
                    inventory, created = Inventory.objects.get_or_create(inventory_raw_material=raw_material_instance,warehouse=ware_house)
                    status,message = inventory.add_stock(amount=decimal_value,user=profile,receipt_number=receipt_number)
                    # print(status,message)

                    if not status:
                        return redirect('error_page')
                
                        

        return redirect('success_page')  # Redirect to a success page
    


    materials = raw_material.objects.all()
    
    # Create a list of dictionaries containing main materials and their ingredients
    materials_with_ingredients = []
    
    for material in materials:
        ingredients = material.components.all()  # Get related ingredients
        if ingredients.exists():
        


            ingredients_list=[]

            for composition in ingredients:


                dic = {"name": composition.ingredient.name,
                        "ratio": composition.ratio ,
                          "quantity":get_total_quantity(composition.ingredient),
                          "id":composition.ingredient.id,
                          "unit":composition.ingredient.unit,
                          "has_discard" : composition.has_discard,
                          } 
                
                ingredients_list.append(dic)




            
            materials_with_ingredients.append({
                "main_material": material.name,
                "ingredients": ingredients_list,
                "id":material.id,
                "unit":material.unit,
                # "has_discard" : material.
            })

    ware_houses = Warehouse.objects.all()
        
    context = {"materials_with_ingredients": materials_with_ingredients,'warehouses':ware_houses}
    return render(request, 'users/store_product.html',context)






@login_required
def take_store(request):



    if request.method == 'POST':
        
        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')
        
        ware_house = None
        if 'warehouse' in data.keys():
            ware_house = data['warehouse']
            data.pop('warehouse','Not found')
        elif ware_house is None:
            return

        profile = Profile.objects.get(id = request.user.id)

        selected_warehouse = Warehouse.objects.get(name = ware_house)

        values ={}






        raw_materials_with_quantity = get_material_quantity(show_all=False,selected_warehouses=selected_warehouse)

        mother_materials = get_mother_material_quantity(show_all=False,selected_warehouses=selected_warehouse,raw_materials_with_quantity=raw_materials_with_quantity)
        if raw_materials_with_quantity is None or mother_materials is None:
            print('error in get_mother_material_quantity')
            return False
        # Serialize your mother_materials data
        materials_data = [
            {
                'id': mother_material.id,
                'name': mother_material.name,
                'describe': mother_material.describe,
                'total_quantity': mother_material.total_quantity,
                'submaterials': [
                    {
                        'id' :  submaterial.id,
                        'name': submaterial.name,
                        'describe': submaterial.describe,
                        'total_quantity': submaterial.total_quantity,
                        'unit': submaterial.unit,
                    }
                    for submaterial in mother_material.mother_material.all()
                ],
            }
            for mother_material in mother_materials
        ]

        # print(time.time()-t)

        return JsonResponse({'mother_materials': materials_data,'backend_endpoint':BACKEND_ENDPOINT})











        messages.success(request,'مقادیر مورد نظر با موفقیت اضافه گردید')
        # return redirect('/profile/my_orders')
        return redirect('success_page')  # Redirect to your desired page

    else:


            ware_houses = Warehouse.objects.all()

            # raw_materials_with_quantity = get_material_quantity(show_all=True)
            # mother_materials = get_mother_material_quantity(material_name='all',show_all=True, raw_materials_with_quantity =  raw_materials_with_quantity)

            return render(request, 'users/store_take.html', {'warehouses':ware_houses,'backend_endpoint':BACKEND_ENDPOINT})
        






@login_required
def confrim_take_store(request):

    if request.method == 'POST':
        try:
            data = dict(request.POST.dict())
            data.pop('csrfmiddlewaretoken','Not found')
            print(data)

            data.pop('csrfmiddlewaretoken','Not found')
            print(data)


            if 'warehouse' in data.keys():
                ware_house = data['warehouse']
                data.pop('warehouse','Not found')
                
            else:
                return

            profile = Profile.objects.get(id = request.user.id)

            ware_house = Warehouse.objects.get(id = ware_house)


            items = json.loads(data['items'])  # Now items is {'119': 2, '124': 12, '133': 2}

            # Iterate through the items and pop them from the model
            
            for item_id in items.keys():
                # try:
                    # Assuming 'id' is the primary key of the Material model
                id  = item_id.split('-')[1]
                raw_material_instance = raw_material.objects.get(id=int(id))
                print(raw_material_instance)

                decimal_value = Decimal(items[item_id])

                inventory, created = Inventory.objects.get_or_create(inventory_raw_material=raw_material_instance,warehouse=ware_house)
                status,message = inventory.remove_stock(amount=decimal_value,user=profile)
                print('status : ',status)
                # if status:
                messages.success(request,message)
                # return redirect('/profile/my_orders')
                return JsonResponse({'status': status, 'message': message})
                # else:
                #     message = status
                #     messages.success(request,message)
                #     # return redirect('/profile/my_orders')
                #     return JsonResponse({'status': 'success', 'message': message})
        except Exception as e:
            # Add error message
            messages.error(request, str(e))
            return JsonResponse({'status': 'error', 'message': str(e)})














@login_required
def show_store(request):

        if request.method == "POST":
             
            t = time.time()
            data = dict(request.POST.dict())
            selected_warehouses = request.POST.getlist('warehouses')
            show_all = request.POST.get('show_all') == 'true'
            show_available = request.POST.get('show_available') == 'true'

            first_key, selected_warehouses = list(data.items())[0]

            if selected_warehouses !='all':
                selected_warehouses = int(selected_warehouses)

            raw_materials_with_quantity = get_material_quantity(show_all=show_all,selected_warehouses=selected_warehouses)

            mother_materials = get_mother_material_quantity(show_all=show_all,selected_warehouses=selected_warehouses,raw_materials_with_quantity=raw_materials_with_quantity)
            if raw_materials_with_quantity is None or mother_materials is None:
                print('error in get_mother_material_quantity')
                return False
            # Serialize your mother_materials data
            materials_data = [
                {
                    'id': mother_material.id,
                    'name': mother_material.name,
                    'describe': mother_material.describe,
                    'total_quantity': mother_material.total_quantity,
                    'submaterials': [
                        {
                            'id' :  submaterial.id,
                            'name': submaterial.name,
                            'describe': submaterial.describe,
                            'total_quantity': submaterial.total_quantity,
                            'unit': submaterial.unit,
                        }
                        for submaterial in mother_material.mother_material.all()
                    ],
                }
                for mother_material in mother_materials
            ]

            print(time.time()-t)

            return JsonResponse({'mother_materials': materials_data,'backend_endpoint':BACKEND_ENDPOINT})

        else:

            t = time.time()

            ware_houses = Warehouse.objects.all()

            raw_materials_with_quantity = get_material_quantity(show_all=True)

            mother_materials = get_mother_material_quantity(material_name='all',show_all=True, raw_materials_with_quantity =  raw_materials_with_quantity)

            print(time.time()-t)
    
            return render(request, 'users/store.html', {'mother_materials': mother_materials,'warehouses':ware_houses,'backend_endpoint':BACKEND_ENDPOINT})
        

def get_material_quantity(material_name = 'all',show_all=False,selected_warehouses = 'all'):

    raw_materials_with_quantity = None            
    if material_name == 'all' and selected_warehouses=='all':

        raw_materials_with_quantity = raw_material.objects.annotate(
                total_quantity=Coalesce(Sum('inventory__quantity'), 0, output_field=DecimalField())
            ).order_by('describe')
        

    elif material_name == 'all' and selected_warehouses != 'all':
                        
        raw_materials_with_quantity = raw_material.objects.annotate(
            total_quantity=Coalesce(
                Sum('inventory__quantity', filter=Q(inventory__warehouse_id=selected_warehouses)),  # Filter by warehouse ID
                0,
                output_field=DecimalField()
            )
                ).order_by('describe')


    if  not(show_all) and raw_materials_with_quantity is not None:

        raw_materials_with_quantity = raw_materials_with_quantity.filter(total_quantity__gt=0)

    return raw_materials_with_quantity



def get_mother_material_quantity(material_name = 'all',show_all=False,selected_warehouses='all',raw_materials_with_quantity=None):

    mother_materials_with_quantity = None

    if material_name == 'all' and selected_warehouses=='all':
        
        if raw_material is None:
            raw_materials_with_quantity = raw_material.objects.annotate(
                total_quantity=Coalesce(Sum('inventory__quantity'), 0, output_field=DecimalField())
            ).order_by('describe')

        # Prefetch raw_materials into mother_materials with the annotated quantity
        mother_materials_with_quantity = MotherMaterial.objects.prefetch_related(
            Prefetch(
                'mother_material',  # Assuming this is the correct related_name to access raw_materials
                queryset=raw_materials_with_quantity,  # Prefetched raw materials with total quantities
            )
        ).annotate(
            total_quantity=Coalesce(Sum('mother_material__inventory__quantity'), 0, output_field=DecimalField())  # Set output_field for the total quantity
        ).order_by('describe')

    elif  material_name == 'all' and selected_warehouses != 'all':
    

        # Prefetch raw materials into mother materials with the annotated quantity for the specific warehouse
        mother_materials_with_quantity = MotherMaterial.objects.prefetch_related(
            Prefetch(
                'mother_material',  # Related name to access raw materials
                queryset=raw_materials_with_quantity,  # Prefetched raw materials with total quantities for warehouse 1
            )
        ).annotate(
            total_quantity=Coalesce(
                Sum('mother_material__inventory__quantity', filter=Q(mother_material__inventory__warehouse_id=selected_warehouses)),  # Filter by warehouse ID
                0,
                output_field=DecimalField()
            )
        ).order_by('describe')
                

    if  not(show_all) and mother_materials_with_quantity is not None:

        mother_materials_with_quantity = mother_materials_with_quantity.filter(total_quantity__gt=0)



    return mother_materials_with_quantity








def log_view_store(request):
    logs = InventoryLog.objects.all().order_by('date').reverse()
    

    # Get users, raw materials, and warehouses for filters
    users = Profile.objects.all()
    raw_materials = RawMaterial.objects.all()
    warehouses = Warehouse.objects.all()

    receipt_number = request.GET.get('receipt_number')

    
    if receipt_number:
        try:
            receipt_number = int(receipt_number)
        except:
            pass
        logs = logs.filter(receipt_Number=receipt_number)


    # Filtering based on request parameters
    user = request.GET.get('user')
    if user and user!='select_all':
        logs = logs.filter(user__id=user)

    change_type = request.GET.get('change_type')
    if change_type:
        logs = logs.filter(change_type=change_type)

    warehouse = request.GET.get('warehouse')
    if warehouse and warehouse !='select_all':
        logs = logs.filter(inventory__warehouse__id=warehouse)

    raw_material = request.GET.get('raw_materials')
    a = request.GET.get('raw_materials')

    if raw_material:
        logs = logs.filter(inventory__inventory_raw_material__id=raw_material)



    # date_from = request.GET.get('date_from')
    # date_to = request.GET.get('date_to')
    # if date_from and date_to:
    #     date_from = convert_georgian2jalali(date_from)
    #     date_to = convert_georgian2jalali(date_to)
    #     logs = logs.filter(date__range=[date_from, date_to])

    # Render the template with logs and filter data
    

    default_user = request.GET.get('user', None)

    # user = Profile.objects.get(id = default_user)
    # default_user = user.user.username
    default_change_type = request.GET.get('change_type', None)
    default_date_from = request.GET.get('date_from', None)
    default_date_to = request.GET.get('date_to', None)
    default_raw_materials = request.GET.getlist('raw_materials', [])
    default_warehouse = request.GET.get('warehouse', None)

    try:
        default_user = int(default_user)
        default_warehouse = int(default_warehouse)
    except:
        pass
    # Context to pass to template
    context = {
        'logs': logs,
        'users': users,
        'warehouses':warehouses,
        'raw_materials':  raw_materials,
        'default_user': default_user,
        'default_change_type': default_change_type,
        'default_date_from': default_date_from,
        'default_date_to': default_date_to,
        'default_raw_materials': default_raw_materials,
        'default_warehouse': default_warehouse
    }


    return render(request, 'users/store_log.html',context)


def convert_georgian2jalali(jdate):

    # Convert the string to JalaliDate object
    # First, convert Persian numbers to English numbers
    persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    jalali_date_str_english = jdate.translate(persian_to_english)

    # Convert to JalaliDate object
# Split the date string to extract year, month, and day
    year, month, day = map(int, jalali_date_str_english.split('/'))

    # Create a JalaliDate object
    jalali_date = JalaliDate(year, month, day)

    # Convert to Gregorian date
    georgian_date = jalali_date.to_gregorian()


    return georgian_date









def register_entry(request, id):
 
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            latitude = float(latitude)
            longitude = float(longitude)

            # Here you can decide if it's an entry or exit based on your logic
            # For example, you might want to check if the user is in an allowed location
            user = User.objects.get(id=id)  # Fetch user by ID
            allowed_locations = AllowedLocation.objects.get(user=user)

            # Check if the latitude and longitude are within the allowed locations
            for location in allowed_locations.locations.all():
                distance = calculate_distance(latitude, longitude, float(Decimal(location.latitude)), float(Decimal(location.longitude)))
                if distance <= location.radius_meters:
                    # Save the location to the database as an entry


                    status = is_user_in(user)

                    if status is not None:
                        status = not status
                    
                    else:
                        status = True

                    log_entry = EntryExitLog.objects.create(
                        user=user,
                        is_entry=status,  # Set to True for entry
                        location=location
                    )

                    translate_status = 'خروج'

                    if status:
                        translate_status = 'ورود'
                    
                    return JsonResponse({'success': True, 'message': '{} شما در {} با موفقیت ثبت گردید'.format(translate_status,location.name)})
            
            return JsonResponse({'success': False, 'message': 'شما در موقعیت صحیح قرار ندارید'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'مشکل در ثبت'})
        

    else:
            
        user = get_object_or_404(User, id=request.user.id)  # Get the user by id
        latest_log = get_latest_exit(user)
        return render(request, 'users/register_entry.html',{'last_status': latest_log })




def get_allowed_locations(request):
    user = request.user  # Get the logged-in user
    try:

        allowed_locations = AllowedLocation.objects.prefetch_related('locations').get(user=user)
        locations = allowed_locations.locations.all()

        # Create a list of locations with lat, long, and radius to send to frontend
        locations_data = [
            {
                'name': location.name,
                'latitude': float(location.latitude),
                'longitude': float(location.longitude),
                'radius': location.radius_meters
            } 
            for location in locations
        ]

        return JsonResponse({'locations': locations_data})
    except AllowedLocation.DoesNotExist:
        return JsonResponse({'locations': []})



def histoty_entry(request,id):

    if request.method == 'POST':
        return

    else:

        obj = UserWorkTimeManager()

        data , total_work = obj.user_work_time(username=request.user.id)


        # data = {
        #     user: dict(sorted(
        #         logs.items(),
        #         key=lambda item: JalaliDatetime.strptime(item[0], '%Y/%m/%d'),
        #         reverse=True  # Sort in descending order
        #     ))
        #     for user, logs in data.items()
        # }


        return render(request,'users/register_history.html',{'user_time_data':data,'total_work':total_work})


#------------------------------------------------------------------ پایان دوران سربازی در 05

########################## شروع مجدد برنامه در تاریخ 15 اذر



def update_prices(request,city,res_name):

    print('city:',city)
    print('res_name:',res_name)



    ret = SnappFoodList.objects.filter(
            name=res_name, city__name=city
        ).first()  # Get the first match
    
    # gp = get_price(res_name=data['name'],res_link=data['link'],city= data['city'])
    # gp.get_name_price()

    if ret is None:
        print('Restaurant link is not in DB')
        return

    res_link = ret.link



    gp = get_price(res_name=res_name,res_link=res_link,city= city)


    gp.get_name_price(update=True)





    print(id)

















def success_page(request):
    return render(request, 'users/success_page.html')  # Render your success page template

def error_page(request):
    return render(request, 'users/error_page.html')  # Render your success page template





def submit_data(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Here you can process the data (e.g., save to database, validate, etc.)
        print(request.POST)

        # Send a JSON response back
        response_data = {
            'name': name,
            'email': email
        }

        return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def show_test(request):

    return render(request, 'users/test.html')
        





def register_exit(request, log_id):
    log = EntryExitLog.objects.get(id=log_id)
    log.exit_time = timezone.now()
    log.save()
    return redirect('profile')  # Redirect to the profile page




