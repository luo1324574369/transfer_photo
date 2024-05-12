"""transfer photo"""

import os
import shutil
from datetime import datetime
import yaml
from PIL import Image
from PIL.ExifTags import TAGS


def main():
    """main function"""

    with open("config.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    src_dir = data["src_dir"]
    target_dir = data["target_dir"]

    last_sync_filename = find_last_sync_filename(target_dir)
    print(f"last sync filename: {last_sync_filename}")

    all_file = combine_files(src_dir)
    for f, files in all_file.items():
        if last_sync_filename != "" and f <= last_sync_filename:
            continue
        transfer(files, target_dir)
    print("end of transfer")


def combine_files(src_dir):
    """combine"""
    all_files = {}
    files = os.listdir(src_dir)
    for file in files:
        file_name, file_ext = os.path.splitext(file)
        if file_ext not in [".JPG", ".CR3"]:
            continue
        if file_name in all_files:
            all_files[file_name][file_ext] = full_filename(src_dir, file)
            continue
        all_files[file_name] = {file_ext: full_filename(src_dir, file)}
    return all_files


def transfer(files, target_dir):
    """transfer file to target directory split by date"""

    ctime = get_ctime_from_file(files[".JPG"])
    if ctime == "":
        ctime = "2001-01-01"

    target_save_dir = full_filename(target_dir, ctime)
    if not os.path.exists(target_save_dir):
        os.mkdir(target_save_dir)

    for _, file in files.items():
        shutil.copy(file, target_save_dir)
        print(f"moved {file} to {target_save_dir}")


def get_ctime_from_file(file):
    """get ctime from file"""
    photo_info = get_photo_info(file)
    if not photo_info:
        return ""
    if "DateTimeOriginal" in photo_info:
        d = datetime.strptime(photo_info["DateTimeOriginal"], "%Y:%m:%d %H:%M:%S")
        return datetime.strftime(d, "%Y-%m-%d")
    return ""


def get_photo_info(photo_path):
    """get photo info"""

    image = Image.open(photo_path)
    exif_data = image._getexif()

    photo_info = {}
    if exif_data:
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            photo_info[tag_name] = value

    return photo_info


def full_filename(d, filename):
    """full filename"""
    return d + "/" + filename


def find_last_sync_filename(target_dir):
    """checkout target directory identified the filename that last time synced"""
    files = os.listdir(target_dir)
    max_dir = ""
    for f in files:
        if not os.path.isdir(full_filename(target_dir, f)):
            continue
        dir_format_date = datetime.strptime(f, "%Y-%m-%d")
        if max_dir == "" or dir_format_date > max_dir:
            max_dir = dir_format_date
    if max_dir == "":
        return ""

    files = os.listdir(full_filename(target_dir, max_dir.strftime("%Y-%m-%d")))
    max_file = ""
    for f in files:
        if max_file == "" or f > max_file:
            max_file = f
    file_name, file_extension = os.path.splitext(max_file)
    return file_name


if __name__ == "__main__":
    main()
