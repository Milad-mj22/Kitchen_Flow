from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from users.models import RestaurantBranch,create_order,NightOrderRemainder,mother_food,Profile,raw_material
# Create your views here.
from .models import OrderStep,MaterialUsage
import ast
from decimal import Decimal

def show_flow(request,order_id):
    if request.method == 'GET':

        context = {
            'order_id': order_id,
        }

        return render(request, 'show_flow.html',context)



def convert_raw_material2object(materials):

    result = {}
    materials_dict = ast.literal_eval(materials)
    # Reverse keys and values
    reversed_dmaterials_dictict = {v: k for k, v in materials_dict.items()}
    for material in list(materials_dict.keys()):

        obj = raw_material.objects.filter(name=material).first()

        


        if material in result.keys():

            obj.quantity_used = float(result[material].quantity_used) + float(materials_dict[material])
        else:
            obj.quantity_used = float(materials_dict[material])

        obj.quantity_used = round(obj.quantity_used,4)



        result[material] = obj
    
    return result



def check_order_confirmed(order , stepNumber:int):

    ret_confirmed =  OrderStep.objects.filter(order = order , step_number=stepNumber).first()
    if ret_confirmed is not None:
        return ret_confirmed
    return False



def get_allowed_confirm_users(stepNumber:int):

    if stepNumber==1:
        allowed_roles = ['manager', 'fishzan']  # Adjust based on your logic
        return allowed_roles

    if stepNumber==2:
        allowed_roles = ['manager', 'fishzan']  # Adjust based on your logic
        return allowed_roles

def section1_view(request,order_id):

    context = {'order_id': order_id}
    step_number = 1

    if request.method == 'POST':

        material_names = request.POST.getlist("materials_names[]")
        material_units = request.POST.getlist("materials_units[]")
        material_quantities = request.POST.getlist("materials_quantities[]")


        ret = create_order.objects.filter(id=order_id).first()

        # order_step_obj = get_object_or_404(OrderStep, step_number=1 , order =ret )

        user_profile = Profile.objects.get(user=request.user)

        order_step_obj, created = OrderStep.objects.get_or_create(
            step_number=1, 
            order=ret,  # Ensure 'ret' is the correct order instance
            confirmed_by = user_profile
        )
        materials_data = []
        for i in range(len(material_names)):
            materials_data.append({
                "name": material_names[i],
                "unit": material_units[i],
                "quantity": material_quantities[i]
            })

            material = get_object_or_404(raw_material, name= material_names[i])  # Find material by name
            
            MaterialUsage.objects.create(
                step=order_step_obj,
                material=material,
                quantity=material_quantities[i]
            )

    


        return JsonResponse({"status": "success"})

    else:

        # ret = create_order.objects.filter(id=order_id).first()
        ret = create_order.objects.filter(id=order_id).first()
        print(ret)
        raw_materials_obj = convert_raw_material2object(ret.content)
        user_profile = Profile.objects.get(user=request.user)
        user_role = user_profile.job_position.name
        allowed_roles = get_allowed_confirm_users(stepNumber=1)
        # Check if the user has access to submit this step
        can_submit = user_role in allowed_roles
        is_confirmed = check_order_confirmed(order=ret,stepNumber=1)
        return render(request, 'section1.html', {
            'material_usages': raw_materials_obj,
            'user_role': user_role,
            'can_submit': can_submit,
            'is_confirmed': is_confirmed,
            'order_id':order_id
        })









def section2_view(request,order_id):
    # should add select ware house that exit and add exist from warehouse
    context = {'order_id': order_id}
    step_number = 2

    if request.method == 'POST':
        
        material_names = request.POST.getlist("materials_names[]")
        material_sent = request.POST.getlist("materials_sent[]")
        
        ret = create_order.objects.filter(id=order_id).first()

        user_profile = Profile.objects.get(user=request.user)

        order_step_obj, created = OrderStep.objects.get_or_create(
            step_number=step_number, 
            order=ret,  # Ensure 'ret' is the correct order instance
            confirmed_by = user_profile
        )
        materials_data = []
        for i in range(len(material_names)):


            material = get_object_or_404(raw_material, name= material_names[i])  # Find material by name
            
            MaterialUsage.objects.create(
                step=order_step_obj,
                material=material,
                quantity=Decimal(float(material_sent[i]))
            )


        return JsonResponse({"status": "success"})



    else:
        ret = create_order.objects.filter(id=order_id).first()
        raw_materials_obj = convert_raw_material2object(ret.content)
        user_profile = Profile.objects.get(user=request.user)
        user_role = user_profile.job_position.name
        allowed_roles = get_allowed_confirm_users(stepNumber=step_number)
        # Check if the user has access to submit this step
        can_submit = user_role in allowed_roles
        is_confirmed = check_order_confirmed(order=ret,stepNumber=step_number)
        return render(request, 'section2.html', {
            'material_usages': raw_materials_obj,
            'user_role': user_role,
            'can_submit': can_submit,
            'is_confirmed': is_confirmed,
            'order_id':order_id
        })





def section3_view(request,order_id):
    return render(request, 'section3.html',{
            'order_id':order_id
        })


def section4_view(request , order_id):

    if request.method == 'POST':


        data = dict(request.POST.dict())
        data.pop('csrfmiddlewaretoken','Not found')

        restaurant = None

        if 'warehouse' in data.keys():
            restaurant = data['warehouse']
            data.pop('warehouse','Not found')
            restaurant = RestaurantBranch.objects.filter(id=restaurant).first()
        else:
            return
        

        order = create_order.objects.filter(id=order_id).first()

        reminder, created = NightOrderRemainder.objects.get_or_create(
            order=order,
            restaurant = restaurant
            )
        
        reminder.remainder_night_order = data

            # Save the reminder to the database
        reminder.save()



        print(data)


        return render(request, 'users/section5.html')

        # restaurant = RestaurantBranch.objects.filter(id = )



    if request.method == 'GET':

        # You can use order_id here
        # For example, you can query the database or pass it to the template
        context = {
            'order_id': order_id
        }

        ret = create_order.objects.filter(id=order_id).first()
        if ret:
            night_order = eval(ret.night_order)

        possible_foods = {}

        for food,value in night_order.items():
            if value>0:
                possible_foods[food]=value


        restaurants = RestaurantBranch.objects.all()

        mother_foods = mother_food.objects.prefetch_related('mother_food_id').all()    



        order = create_order.objects.filter(id=order_id).first()

        remainder = NightOrderRemainder.objects.filter(
            order=order,
            ).first()
        if remainder is not None:
            if remainder.remainder_night_order is not None:
                defult_values = eval(remainder.remainder_night_order)
                # Filter Foods within each mother_food
                filter_names = []
                copy = mother_foods
                for mother_food in mother_foods:
                    final_foods = []
                    total_order = 0
                    print('mother_food',mother_food)
                    for food in mother_food.mother_food_id.all():
                        if food.name in list(possible_foods.keys()):

                            if food.name in defult_values.keys():
                                df_value = defult_values[food.name]
                            else:
                                df_value = 0

                            data = {
                                'id' : food.id,
                                'name' : food.name,
                                'defult_value' : df_value,
                                'order' : possible_foods[food.name]
                            }

                            total_order+=possible_foods[food.name]

                            final_foods.append(data)

                    if final_foods ==[]:

                        copy = copy.exclude(name=mother_food.name)
                        
                    else:
                        mother_food.final_foods = final_foods
                        mother_food.total = total_order
                        filter_names.append(mother_food.name)


                        food = copy.filter(name = mother_food.name)
                        food = mother_food
                

                        # copy

        return render(request, 'section4.html', context={'order_id':order_id,'possible_foods':possible_foods,'restaurants':restaurants,'mother_foods': mother_foods})








def section5_view(request,order_id):
    return render(request, 'section5.html',{
            'order_id':order_id
        })

