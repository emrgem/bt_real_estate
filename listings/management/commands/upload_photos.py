import os
from django.core.management.base import BaseCommand
from supabase import create_client
from django.conf import settings
from storage3.exceptions import StorageApiError

class Command(BaseCommand):
    help = "Recursively upload existing images from media/photos/ and all subfolders to Supabase Storage"

    def handle(self, *args, **kwargs):
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        media_folder = os.path.join(settings.MEDIA_ROOT, "photos")

        if not os.path.exists(media_folder):
            self.stdout.write(self.style.ERROR(f"❌ Media folder {media_folder} does not exist."))
            return

        # Walk through all subdirectories and upload files
        for root, _, files in os.walk(media_folder):
            for filename in files:
                file_path = os.path.join(root, filename)  # Full local file path

                if os.path.isfile(file_path):  # Ensure it's a file
                    # Get the relative path inside `photos/` to maintain subfolder structure
                    relative_path = os.path.relpath(file_path, media_folder)  # e.g., "2024/12/12/image.jpg"
                    supabase_path = f"photos/{relative_path}".replace("\\", "/")  # ✅ Fix Windows backslashes

                    print(f"📤 Checking {supabase_path} in Supabase...")

                    # Get parent folder path for checking file existence
                    folder_path = os.path.dirname(supabase_path)
                    file_name = os.path.basename(supabase_path)
                    
                    try:
                        # Check if file exists by listing its parent directory
                        existing_files = supabase.storage.from_("media").list(folder_path)
                        existing_file_names = [file["name"] for file in existing_files]
                        
                        if file_name in existing_file_names:
                            print(f"🔄 File {supabase_path} already exists. Skipping.")
                            continue
                            
                        # Upload File to Supabase
                        print(f"📤 Uploading {relative_path} to Supabase as {supabase_path}...")

                        with open(file_path, "rb") as file:
                            response = supabase.storage.from_("media").upload(
                                supabase_path, file, file_options={"content-type": "image/jpeg"}
                            )
                            self.stdout.write(self.style.SUCCESS(f"✅ Uploaded {relative_path} successfully!"))
                            
                    except StorageApiError as e:
                        self.stdout.write(self.style.ERROR(f"⚠️ Upload error for {relative_path}: {e}"))
                        # If the error is about parent folders not existing, we need to create them
                        if "The resource's parent does not exist" in str(e):
                            try:
                                print(f"🗂️ Creating parent folder structure for {folder_path}...")
                                # Upload an empty file to create the folder structure
                                empty_file = b""
                                placeholder_path = f"{folder_path}/.placeholder"
                                supabase.storage.from_("media").upload(
                                    placeholder_path, empty_file
                                )
                                # Try upload again
                                with open(file_path, "rb") as file:
                                    supabase.storage.from_("media").upload(
                                        supabase_path, file, file_options={"content-type": "image/jpeg"}
                                    )
                                    self.stdout.write(self.style.SUCCESS(f"✅ Uploaded {relative_path} after creating folder!"))
                            except Exception as folder_error:
                                self.stdout.write(self.style.ERROR(f"❌ Failed to create folder structure: {folder_error}"))

        self.stdout.write(self.style.SUCCESS("🎉 All images from media/photos/ and subfolders uploaded to Supabase!"))