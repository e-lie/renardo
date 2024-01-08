import os
import pathlib
import requests
from sys import platform
from bs4 import BeautifulSoup
from datetime import datetime

class SampleDownloadError(Exception):
    pass

SAMPLES_FOLDER_PATH = None

# default config path
# on windows AppData/Roaming/renardo
# on Linux ~/.config/renardo
# on MacOS /Users/<username>/Library/Application Support/renardo
if platform == "linux" or platform == "linux2" :
    home_path = pathlib.Path.home()
    SAMPLES_FOLDER_PATH = home_path / '.config' / 'renardo' / 'samples'
elif platform == "darwin":
    home_path = pathlib.Path.home()
    SAMPLES_FOLDER_PATH = home_path / 'Library' / 'Application Support' / 'renardo' / 'samples'
elif platform == "win32":
    appdata_roaming_path = pathlib.Path(os.getenv('APPDATA'))
    SAMPLES_FOLDER_PATH = appdata_roaming_path / 'renardo' / 'samples'

def download_samples_pack(samples_pack_name="foxdot_default"):
    base_url = f"https://samples.renardo.org/{samples_pack_name}/"
    os.makedirs(SAMPLES_FOLDER_PATH / samples_pack_name, exist_ok=True)
    directory_links = []
    audiofile_links = []
    print("Scanning samples pack...")
    find_audio_links_recursive(base_url, directory_links, audiofile_links)
    # print(audiofile_links)

    for directory in directory_links:
        os.makedirs(SAMPLES_FOLDER_PATH / samples_pack_name / directory, exist_ok=True)
        # print(SAMPLES_FOLDER_PATH / samples_pack_name / directory)

    for audiofile in audiofile_links:
        download_file(audiofile, base_url, SAMPLES_FOLDER_PATH / samples_pack_name)

    with open(SAMPLES_FOLDER_PATH / samples_pack_name / 'downloaded_at.txt', mode="w") as file:
        file.write(str(datetime.now()))

def create_renardo_config_directory():
    if not os.path.exists(SAMPLES_FOLDER_PATH):
        os.makedirs(SAMPLES_FOLDER_PATH)

def get_sample_folder_path():
    return SAMPLES_FOLDER_PATH

def download_file(audiofile_relative_path, base_url, base_download_dir):
    url = base_url + audiofile_relative_path
    # try:
    # error should rather be catched by the download pack function
    response = requests.get(url)
    if response.status_code != 200:
        raise SampleDownloadError
    if "content-disposition" in response.headers:
        content_disposition = response.headers["content-disposition"]
        filename_full = content_disposition.split("filename=")[1]
        filename = filename_full.split("/")[-1]
    else:
        filename = url.split("/")[-1]
    with open(base_download_dir / audiofile_relative_path, mode="wb") as file:
        file.write(response.content)
    print(f"Downloaded file {filename}")
    # except Exception:
    #     print(f"Error downloading the file: {url}")

def link_is_directory(url):
    return url.endswith('/')

def renardo_samples_initialized():
    return os.path.exists(SAMPLES_FOLDER_PATH / 'foxdot_default' / 'downloaded_at.txt')

def find_audio_links_recursive(base_url, directory_links, audiofile_links, current_path=''):
    page = requests.get(base_url+current_path).content
    bsObj = BeautifulSoup(page, 'html.parser')
    maybe_directories = bsObj.findAll('a', href=True)
    for link in maybe_directories:
        # print(f"link : {link['href']}")
        # print(link_is_directory(link['href']))
        if link_is_directory(link['href']) and link["href"] != '../':
            new_path = current_path + link['href']
            directory_links.append(new_path)      
            find_audio_links_recursive(base_url, directory_links, audiofile_links, current_path=new_path)
        else:
            if(link['href'].endswith('.wav')):
                # print(link['href'])
                audiofile_links.append(current_path + link['href'])

def main():
    pass
    #download_samples_pack()
