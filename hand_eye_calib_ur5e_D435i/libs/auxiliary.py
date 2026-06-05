import logging
import platform
import subprocess
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import re

from libs.log_setting import CommonLog

logger_ = logging.getLogger(__name__)
logger_ = CommonLog(logger_)


def ping(ip):

    if platform.system().lower() == 'windows':
        ping_cmd = f'ping -n 1 {ip}'
    else:
        ping_cmd = ["ping","-c","1",f"{ip}"]


    logger_.info(f'command:{ping_cmd}')


    response = subprocess.run(ping_cmd, stdout=subprocess.PIPE)

    if response.returncode == 0:
        return True
    else:
        return False


def get_ip():

    ip1 = "172.31.1.200" # must check actual UR5e IP
    
    if ping(ip1):

        print(f"Successfully pinged {ip1}")
        return ip1

    else:

        print("Unable to ping IP addresses")
        return False


def create_folder_with_date():


    # date format: YYYYMMDD
    today = datetime.now().strftime('%Y%m%d')

    prefix_files = "eye_hand_data"


    base_folder_name = os.path.join(prefix_files,f"data{today}")


    index = 0
    folder_path = base_folder_name


    while os.path.exists(folder_path):
        index += 1
        folder_path = f"{base_folder_name}{str(index).zfill(2)}"




    os.makedirs(folder_path)
    logger_.info(f"create folder {folder_path}")
    return folder_path

def popup_message(title, message):


    root = tk.Tk()
    root.withdraw()  


    root.attributes('-topmost', True)


    messagebox.showinfo(title, message)


    root.destroy()


def find_latest_data_folder(path):

    # folder name "dataYYYYMMDD"
    pattern = re.compile(r'^data(\d{8})(\d*)$')

    folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f)) and pattern.match(f)]


    if not folders:
        return None

    print(folders)


    folders.sort(key=lambda x: (pattern.match(x).group(1), pattern.match(x).group(2)), reverse=True)


    return folders[0]

if __name__ == "__main__":

    create_folder_with_date()
