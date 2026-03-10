import shutil
import os

os.makedirs("backup", exist_ok=True)

shutil.copy("sample.txt", "backup/sample.txt")

print("File copied to backup directory.")

shutil.move("backup/sample.txt", "backup/moved_sample.txt")

print("File moved and renamed.")