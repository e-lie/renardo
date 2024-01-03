from sys import platform
import pathlib
from os import getenv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


# default path : REAPER as example
# on windows AppData/Roaming/REAPER
# on Linux ~/.config/REAPER
# on MacOS /Users/<username>/Library/Application Support/REAPER

import os

SAMPLES_FOLDER_PATH = None

if platform == "linux" or platform == "linux2" :
    home_path = pathlib.Path.home()
    SAMPLES_FOLDER_PATH = home_path /'.config'/'renardo'/'samples'
elif platform == "darwin":
    home_path = pathlib.Path.home()
    SAMPLES_FOLDER_PATH = home_path / 'Library' / 'Application Support' / 'renardo'/'samples'
elif platform == "win32":
    appdata_roaming_path = getenv('APPDATA')
    SAMPLES_FOLDER_PATH = appdata_roaming_path / 'renardo'/'samples'

def download_samples_pack(sample_pack_name="FoxDot"):
    pass
    
def create_renardo_config_directory():
    if not os.path.exists(SAMPLES_FOLDER_PATH):
        os.makedirs(SAMPLES_FOLDER_PATH)

def get_sample_folder_path():
    return SAMPLES_FOLDER_PATH

def download_file(url, destination_folder=SAMPLES_FOLDER_PATH):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception
        if "content-disposition" in response.headers:
            content_disposition = response.headers["content-disposition"]
            filename_full = content_disposition.split("filename=")[1]
            filename = filename_full.split("/")[-1]
        else:
            filename = url.split("/")[-1]
        with open(destination_folder / filename, mode="wb") as file:
            file.write(response.content)
        print(f"Downloaded file {filename}")
    except Exception:
        print(f"Error downloading the file: {url}")

def download_pack(pack_name='foxdot_default'):

    base_url = f"https://samples.renardo.org/{pack_name}/"

    urls = []

    with ThreadPoolExecutor()   as executor:
        executor.map(download_file, urls)

def link_is_directory(url):
    if(url.endswith('/')):
        return True
    else:
        return False

def find_audio_links_recursive(url):
    page = requests.get(url).content
    bsObj = BeautifulSoup(page, 'html.parser')
    maybe_directories = bsObj.findAll('a', href=True)

    for link in maybe_directories:
        # print(link['href'])
        # print(link_is_directory(link['href']))
        if link_is_directory(link['href']) and link["href"] != '../':
            new_url = url + link['href']
            print(new_url)      
            find_audio_links_recursive(new_url)
        else:
            if(link['href'].endswith('.wav')):
                pass
                print(link['href'])
                # print("GOTCHA!") #now safe and download

def main():
    # create_renardo_config_directory()
    # download_file(url="https://github.com/Qirky/FoxDot/raw/master/FoxDot/snd/a/lower/gb_hihat%200.wav")
    find_audio_links_recursive("https://samples.renardo.org/")
    # download_pack()

if __name__ == '__main__':
    main()
