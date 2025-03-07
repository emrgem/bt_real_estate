from django.db import models
from datetime import datetime
from realtors.models import Realtor



from django.db import models
import os
from supabase import create_client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MEDIA_URL = f"{SUPABASE_URL}/storage/v1/object/public/media/"

class UploadedFile(models.Model):
    image = models.ImageField(upload_to="uploads/")

    def save(self, *args, **kwargs):
        if not self.image:
            super().save(*args, **kwargs)
            return

        file_name = self.image.name  # Example: "myphoto.jpg"
        subfolder_path = f"photos/{file_name}"  # Now it goes into 'media/photos/'

        file_data = self.image.file  # File data

        print(f"Uploading {file_name} to Supabase in 'photos/' subfolder...")

        # Upload to Supabase inside the "photos/" folder
        response = supabase.storage.from_("media").upload(subfolder_path, file_data)

        if "error" in response:
            print(f"Upload failed: {response['error']}")
        else:
            print(f"File uploaded successfully: {MEDIA_URL}{subfolder_path}")
            self.image = f"{MEDIA_URL}{subfolder_path}"  # Store URL in database

        super().save(*args, **kwargs)




# Create your models here.
class Listing(models.Model):
    realtor = models.ForeignKey(Realtor, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
    garage = models.IntegerField()
    sqft = models.IntegerField()
    lot_size = models.DecimalField(max_digits=5, decimal_places=2)
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/') #save inside media folder under date structure
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_5 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_6 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    is_published = models.BooleanField(default = True)
    list_date = models.DateTimeField(default = datetime.now, blank=True)
    
    def __str__(self):
        return self.title
    
    