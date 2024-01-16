import os
from datetime import datetime
from indexed import IndexedOrderedDict

import requests
from bs4 import BeautifulSoup

from renardo_gatherer.config_dir import SAMPLES_DIR_PATH

SAMPLES_DOWNLOAD_SERVER = 'https://samples.renardo.org'
DEFAULT_SAMPLES_PACK_NAME = '0_foxdot_default'
LOOP_SUBDIR = '_loop_'

class SampleDownloadError(Exception):
    pass

nonalpha = {"&" : "ampersand",
            "*" : "asterix",
            "@" : "at",
            "\\" : "backslash",
            "|" : "bar",
            "^" : "caret",
            ":" : "colon",
            "$" : "dollar",
            "=" : "equals",
            "!" : "exclamation",
            "/" : "forwardslash",
            "#" : "hash",
            "-" : "hyphen",
            "<" : "lessthan",
            "%" : "percent",
            "+" : "plus",
            "?" : "question",
            ";" : "semicolon",
            "~" : "tilde",
            "1" : "1",
            "2" : "2",
            "3" : "3",
            "4" : "4" }


class SPack:
    '''Type Samples Pack to describe this resource and avoid string -> pattern conversion in Player'''

    def __init__(self, name):
        self.name = name
        self.path = SAMPLES_DIR_PATH / name
        self.loop_path = self.path / LOOP_SUBDIR

    def sample_path_from_symbol(self, symbol):
        """ Return the sample search directory for a symbol """
        sample_path = None
        if symbol.isalpha():
            low_up_dirname = 'upper' if symbol.isupper() else 'lower'
            sample_path = self.path / symbol.lower() / low_up_dirname
        elif symbol in nonalpha:
            longname = nonalpha[symbol]
            sample_path = self.path / '_' / longname
        return sample_path

    def download_finished(self):
        return (self.path / "downloaded_at.txt").exists()

    def download_file(self, audiofile_relative_path):
        url = f'{SAMPLES_DOWNLOAD_SERVER}/{self.name}' + audiofile_relative_path
        response = requests.get(url)
        if response.status_code != 200:
            raise SampleDownloadError
        if "content-disposition" in response.headers:
            content_disposition = response.headers["content-disposition"]
            filename_full = content_disposition.split("filename=")[1]
            filename = filename_full.split("/")[-1]
        else:
            filename = url.split("/")[-1]
        with open(self.path / audiofile_relative_path, mode="wb") as file:
            file.write(response.content)
        print(f"Downloaded file {filename}")

class SPackManager:
    def __init__(self):
        self._samples_packs = IndexedOrderedDict() # usefull to access from key OR index directly

        if (SAMPLES_DIR_PATH / 'foxdot_default').exists() and not (SAMPLES_DIR_PATH/DEFAULT_SAMPLES_PACK_NAME).exists():
            (SAMPLES_DIR_PATH / 'foxdot_default').rename(SAMPLES_DIR_PATH / DEFAULT_SAMPLES_PACK_NAME)

        if not (SAMPLES_DIR_PATH / DEFAULT_SAMPLES_PACK_NAME / 'downloaded_at.txt').exists():
            self.download_samples_pack(samples_pack_name=DEFAULT_SAMPLES_PACK_NAME)
        else:
            self.add_samples_pack(SPack(DEFAULT_SAMPLES_PACK_NAME))

        self.scan_existing_samples_pack()

    def default_spack(self):
        return self.get_spack(0)

    def renardo_samples_initialized(self) -> bool:
        return self.default_spack().download_finished()

    def scan_existing_samples_pack(self):
        for dir in [f for f in SAMPLES_DIR_PATH.iterdir() if f.is_dir() and f.name != DEFAULT_SAMPLES_PACK_NAME]:
            spack = self.add_samples_pack(SPack(dir.name))

    def add_samples_pack(self, samples_pack: SPack):
        self._samples_packs[samples_pack.name] = samples_pack
        return samples_pack

    def get_spack(self, num_or_SPack) -> SPack:
        return (
            self._samples_packs.values()[num_or_SPack]
            if isinstance(num_or_SPack, int)
            else self._samples_packs[SPack.__name__]
        )

    def download_samples_pack(self, samples_pack_name):
        # if download fails sample pack + folder exists but without downloaded_at.txt file
        samples_pack = self.add_samples_pack(SPack(samples_pack_name))

        base_url = f"{SAMPLES_DOWNLOAD_SERVER}/{samples_pack.name}/"
        directory_links = []
        audiofile_links = []
        print("Scanning samples pack...")
        self.find_audio_links_recursive(base_url, directory_links, audiofile_links)
        # print(audiofile_links)

        for subdir in directory_links:
            (SAMPLES_DIR_PATH / samples_pack_name / subdir).mkdir(parents=True, exist_ok=True)

        for audiofile in audiofile_links:
            samples_pack.download_file(audiofile, base_url)

        with open(SAMPLES_DIR_PATH / samples_pack_name / 'downloaded_at.txt', mode="w") as file:
            file.write(str(datetime.now()))

    def link_is_directory(self, url):
        return url.endswith('/')

    def find_audio_links_recursive(self, base_url, directory_links, audiofile_links, current_path=''):
        page = requests.get(base_url+current_path).content
        bsObj = BeautifulSoup(page, 'html.parser')
        maybe_directories = bsObj.findAll('a', href=True)
        for link in maybe_directories:
            # print(f"link : {link['href']}")
            # print(link_is_directory(link['href']))
            if self.link_is_directory(link['href']) and link["href"] != '../':
                new_path = current_path + link['href']
                directory_links.append(new_path)
                self.find_audio_links_recursive(base_url, directory_links, audiofile_links, current_path=new_path)
            else:
                if(link['href'].endswith('.wav')):
                    # print(link['href'])
                    audiofile_links.append(current_path + link['href'])
