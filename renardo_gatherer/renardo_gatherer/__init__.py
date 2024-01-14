import os

from renardo_gatherer.config_dir import SAMPLES_DIR_PATH
from renardo_gatherer.samples_download import DEFAULT_SAMPLES_PACK_NAME

def get_samples_dir_path():
    return SAMPLES_DIR_PATH

def main():
    pass


# def get_spack_dirname_from_num(spack_num):
#     '''associate samples pack directory names in sample folder with pack numbers'''
#     samples_pack_dirname = ('foxdot_default' if str(spack_num) == '0'
#                             else str(spack_num))
#     return samples_pack_dirname
