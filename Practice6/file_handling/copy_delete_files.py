import shutil
import os

shutil.copy("sample.txt", "sample_copy.txt")
print("File copied")

shutil.copy("sample.txt", "sample_backup.txt")
print("Backup created")

file_to_delete = "sample_copy.txt"

if os.path.exists(file_to_delete):
    os.remove(file_to_delete)
    print("File deleted")
else:
    print("File not found")
