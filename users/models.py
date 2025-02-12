from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django_quill.fields import QuillField

from tinymce.models import HTMLField
from users.fields import JalaliDateField  # Adjust the import path as needed
from phonenumber_field.modelfields import PhoneNumberField
from khayyam import JalaliDatetime

class jobs(models.Model):
    name = models.CharField(max_length=200)
    persian_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3,unique=True)
    describe = models.CharField(max_length=800)
    level = models.IntegerField()

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-short_name']





# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(max_length=100,blank=True)
    last_name = models.TextField(max_length=100,blank=True)
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    address = models.TextField(max_length=300,blank=True,null=True)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()
    # job_position = models.CharField(max_length=400)
    job_position = models.ForeignKey(jobs, on_delete= models.CASCADE,related_name='job_position',default=1,blank=True,null=True)


    def __str__(self):
        return self.user.username

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 800 or img.width > 800:
            max_size=(800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(self.avatar.path)



STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts')
    updated_on = models.DateTimeField(auto_now= True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        print(reverse("blog/", kwargs={"slug": self.slug}))
        # asd
        return "blog/"+{"slug": self.slug}



class Tools(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-title']

    def __str__(self):
        return self.title
    


class FoodFilter(models.Model):


    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-title']

    def __str__(self):
        return self.title




class QuillPost(models.Model):
    content = QuillField()


class Post_quill(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts_quil',default=1,blank=True,null=True)
    body = QuillField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title    
    

    class Meta:
        ordering = ['-created_at']





class full_post(models.Model): 
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='blog_posts_tinymce',default=1,blank=True,null=True)
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ['-created_at']

class cities(models.Model):

    name = models.CharField(max_length=200)
    persian_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=3,unique=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-short_name']

class Projects(models.Model):
    name = models.CharField(max_length=200)
    persian_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=10,unique=True)
    start_date = models.DateTimeField(null=False)
    project_maanger = models.ForeignKey(User, on_delete= models.CASCADE,related_name='project_manager',default=1,blank=True,null=True)
    city = models.ForeignKey(cities, on_delete= models.CASCADE,related_name='project_city',default=1,blank=True,null=False)
    describe = models.CharField(max_length=800)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-short_name']



class PhoneBook(models.Model):
    
    first_name = models.CharField(max_length=200,null=False)
    last_name = models.CharField(max_length=200,null=False)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    description = models.CharField(max_length=3000,null=True,blank=True)
    project = models.ForeignKey(Projects, on_delete= models.CASCADE,related_name='project',default=1,blank=True,null=True)
    position = models.CharField(max_length=3000)

    def __str__(self):
        return str(self.first_name)
    
    class Meta:
        ordering = ['-first_name']



class mode_raw_materials(models.Model):

    name =  models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-name']


class mother_material(models.Model):


    name = models.CharField(max_length=200)
    describe = models.CharField(max_length=800)
    mode = models.ForeignKey(mode_raw_materials,default=None, on_delete= models.CASCADE,related_name='mode_raw_materials_mother_material',blank=True,null=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['describe']





class raw_material(models.Model):

    name = models.CharField(max_length=200)
    describe = models.CharField(max_length=800)
    unit = models.CharField(max_length=200)

    mother = models.ForeignKey(mother_material, on_delete= models.CASCADE,related_name='mother_material',blank=True,null=True)
    mode = models.ForeignKey(mode_raw_materials,default=None, on_delete= models.CASCADE,related_name='mode_raw_materials',blank=True,null=True)



    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['describe']







class create_order(models.Model):


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete= models.CASCADE,related_name='user_create_order',blank=True,null=True)



    content = HTMLField()

    night_order = models.CharField(max_length=20000,blank=True,null=True)

    

    def __str__(self):
        return str(self.created_at)
    
    class Meta:
        ordering = ['-created_at']
    

class SnappFoodList(models.Model):


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(cities, on_delete= models.CASCADE,related_name='city_name',blank=True,null=True)
    name = models.CharField(max_length=200)
    link = models.CharField(max_length=20000)


    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-name']





class mother_food(models.Model):


    name = models.CharField(max_length=200)
    # describe = models.CharField(max_length=800)
    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['-name']




class FoodRawMaterial(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mother = models.ForeignKey(mother_food, on_delete= models.CASCADE,related_name='mother_food_id',blank=True,null=True)
    name = models.CharField(max_length=200)
    data = models.JSONField(blank=True,null=True)
    price = models.IntegerField(default=0,blank=True,null=True)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)  # Added field for image
    details = models.CharField(max_length=2000,default='',blank=True,null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)  # Discount percentage

    def __str__(self):
        return str(self.name)

    def discounted_price(self):
        """
        Calculates the price after applying the discount.
        If discount is set to 0, returns the original price.
        """
        if self.discount > 0:
            discount_amount = (self.discount / 100) * self.price
            return self.price - discount_amount
        return self.price

    class Meta:
        ordering = ['-name']




class Warehouse(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)  # ظرفیت انبار



    def __str__(self):
        return self.name
    
    



class InputReceipt(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # تاریخ ثبت فاکتور
    updated_at = models.DateTimeField(auto_now=True)  # تاریخ آخرین ویرایش
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='input_receipts')  # انبار مربوطه
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_input_receipts', blank=True, null=True)  # کاربری که این فاکتور را ثبت کرده است
    description = models.TextField(blank=True, null=True)  # توضیحات فاکتور

    def __str__(self):
        return f"Receipt {self.id} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']










class Inventory(models.Model):
    inventory_raw_material = models.ForeignKey(raw_material, on_delete=models.CASCADE, related_name='inventory')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='inventories', default=1)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)  # مقدار پیش‌فرض برای quantity
    last_updated = models.DateTimeField(default=timezone.now)
    receipt_Number = models.IntegerField( null=True,blank=True, default=0)


    def add_stock(self, amount,user,receipt_number):
        """افزودن کالا به انبار و ایجاد لاگ به‌طور خودکار"""
        self.quantity += amount
        self.last_updated = timezone.now()
        self.receipt_Number = receipt_number  # ذخیره شماره فیش
        self.save()
        InventoryLog.objects.create(inventory=self, change_type='ADD', amount=amount,user=user,receipt_Number = self.receipt_Number)

    def remove_stock(self, amount,user,receipt_number):
        """برداشتن کالا از انبار و ایجاد لاگ به‌طور خودکار"""
        if self.quantity >= amount:
            self.quantity -= amount
            self.last_updated = timezone.now()
            self.receipt_Number = receipt_number  # ذخیره شماره فیش
            self.save()
            InventoryLog.objects.create(inventory=self, change_type='REMOVE', amount=amount,user=user,receipt_Number = self.receipt_Number)
            return True , 'مقادیر مورد نظر با موفقیت حذف گردید'
        else:
            # raise ValueError("موجودی کافی نیست.")
            return False , 'موجودی کافی نیست'
            

    def __str__(self):
        return f"{self.inventory_raw_material.name} - {self.quantity} in {self.warehouse.name}"




class InventoryLog(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='logs')
    change_type = models.CharField(max_length=10, choices=(('ADD', 'افزودن'), ('REMOVE', 'برداشتن')))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(Profile, on_delete= models.CASCADE,related_name='user_inventory_log',blank=True,null=True,default=1)
    receipt_Number = models.IntegerField( null=True,blank=True, default=0)


    def jalali_date(self):
        return JalaliDatetime(self.date).strftime('%Y/%m/%d %H:%M:%S')

    def __str__(self):
        return f"{self.inventory.inventory_raw_material.name} - {self.change_type} - {self.amount} in {self.inventory.warehouse.name}"






class RestaurantBranch(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)  # ظرفیت انبار



    def __str__(self):
        return self.name



class NightOrderRemainder(models.Model):
    order = models.ForeignKey(create_order, on_delete=models.CASCADE, related_name='night_order_remainders')
    restaurant = models.ForeignKey(RestaurantBranch , on_delete=models.CASCADE, related_name='night_order_remainders')
    remainder_night_order = models.CharField(max_length=20000,blank=True,null=True)


    def __str__(self):
        return f"Order: {self.order} - Restaurant: {self.restaurant.name}"  # or self.restaurant.__str__()

    class Meta:
        ordering = ['order']






# Location model to store location details
class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=14, decimal_places=9)
    longitude = models.DecimalField(max_digits=14, decimal_places=9)
    radius_meters = models.FloatField()  # Radius around these locations within which users are allowed


    def __str__(self):
        return self.name





class AllowedLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    locations = models.ManyToManyField(Location, related_name='allowed_locations')

    def __str__(self):
        return f"Allowed locations for {self.user.username}"


class EntryExitLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='Entry_log')
    timestamp = models.DateTimeField(default=timezone.now)  # This will store both entry and exit times
    is_entry = models.BooleanField(default=True)  # True for entry, False for exit

    location = models.ForeignKey(Location,on_delete=models.CASCADE, related_name='Entry_locations')



    def jalali_date(self):
        return JalaliDatetime(self.timestamp).strftime('%Y/%m/%d') 

    


    def __str__(self):
        event_type = 'Entry' if self.is_entry else 'Exit'
        return f"{self.user.username} - {event_type} at {self.timestamp}"








class CapturedImage(models.Model):
    image = models.ImageField(upload_to="captured_images/")
    created_at = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=200)

    def __str__(self):
        return f"Image {self.id} - {self.image.url}"