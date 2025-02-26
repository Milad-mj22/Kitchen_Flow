from django.urls import path
from .views import error_page, home, material_composition_view, profile, RegisterView,tools \
        ,my_orders,add_raw_material,post_edit_quil\
        ,create_order,add_mother_material,show_order,snapp,show_restaurant_list,\
        restaurant_food_list,add_restaurant,print_order,foodRawMaterials,addfoodrawmaterial,show_food_material,night_food_order,\
        load_temp,CustomLogoutView,add_store,success_page,\
        show_store,submit_data,show_test,take_store,confrim_take_store,log_view_store,\
        register_entry,register_exit,get_allowed_locations,histoty_entry,update_prices, show_night_order_material

        

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile, name='users-profile'),
    path('tools/',tools, name='tools'),
    path('tools/snapp',snapp, name='tools'),
    path('tools/foodrawmaterials',foodRawMaterials, name='foodRawMaterials'),
    path('tools/foodrawmaterials/<int:id>',show_food_material, name='foodRawMaterials'),
    path('tools/add_food_raw_material',addfoodrawmaterial, name='addfoodrawmaterial'),

    # path('tools/snapp/اصفهان/<str:res_name>',restaurant_food_list, name='tools'),

    
    path('tools/snapp/add_restaurant',add_restaurant, name='tools'),
    path('tools/snapp/<str:city>',show_restaurant_list, name='tools'),
    # path('tools/snapp/<str:city>/<str:res_name>',restaurant_food_list, name='tools'),
    path('tools/snapp/<str:city>/<str:res_name>',restaurant_food_list, name='tools'),
    path('tools/snapp/<str:city>/<str:res_name>/update_prices',update_prices, name='tools'),


    path('orders/print_order/<int:id>', print_order, name='order-show'),


    
    path('profile/create_order', create_order, name='create_post'),
    path('profile/my_orders', my_orders, name='my_posts'),
    path('profile/create_material/', add_raw_material, name='add_material'),
    path('profile/create_mother_material/', add_mother_material, name='add_mother_material'),
    path('profile/night_order/', night_food_order, name='night_food_order'),
    path('profile/night_order/null', night_food_order, name='night_food_order'),
    path('profile/show_night_order_material', show_night_order_material, name='show_night_order_material'),
    path('profile/show_night_order_material/submit', night_food_order, name='show_night_order_material_submit'),
    # path('tools/<slug:slug>/',PostDetail.as_view(), name='post_detail'),
    path('orders/edit_order/<int:id>', post_edit_quil, name='order-edit'),
    path('orders/show_order/<int:id>', show_order, name='order-show'),
    path('posts/<int:id>/', post_edit_quil, name='post-edit'),
    path('test/', load_temp, name='post-create3'),

    ################### STORE
    path('profile/store_add/',add_store,name='add-store'),
    path('profile/store_product/',material_composition_view,name='product-store'),
    path('profile/store_take/',take_store,name='add-store'),
    path('profile/store_take_confirm/',confrim_take_store,name='add-store'),
    path('profile/store/',show_store,name='add-store'),
    path('profile/store_log/', log_view_store, name='logs_store'),
    # path('profile/store_product/', product_store, name='product_store'),
    #////////////////////////////////////
# profile/{{user.id}}/register_entry
    path('profile/<int:id>/register_entry/', register_entry, name='register_entry'),
    path('profile/<int:id>/history_entry/', histoty_entry, name='register_entry'),
    # path('profile/<int:id>/register_entry/', register_exit, name='register_exit'),
    path('get_allowed_locations/', get_allowed_locations, name='register_entry'),

    



    path('success/', success_page, name='success_page'),  # URL for success page
    path('error/', error_page, name='error_page'),  # URL for error page
    path('submit-warehouse/', show_store, name='submit-warehouse'),
    path('submit-data/', submit_data, name='submit_data'),
    path('show_test/', show_test, name='submit_data'),
    #/////////////////////////



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
