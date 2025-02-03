
# Expose all
# import renardo_gatherer.config_dir
# import renardo_gatherer.collection_download
# from renardo_gatherer.sample_management import sample_file, sample_category, sample_pack, sample_pack_dict, default_samples

# Expose effectively used only

from renardo_gatherer.config_dir import get_samples_dir_path
from renardo_gatherer.sample_management.sample_pack_library import SamplePackLibrary, sample_pack_library
from renardo_gatherer.sample_management.sample_file import SampleFile
from renardo_gatherer.sample_management.sample_category import nonalpha
from renardo_gatherer.sample_management.default_samples import is_default_spack_initialized, download_default_sample_pack, default_loop_path, LOOP_SUBDIR

# def main():
    # pass

# def get_spack_dirname_from_num(spack_num):
#     '''associate samples pack directory names in sample folder with pack numbers'''
#     samples_pack_dirname = ('foxdot_default' if str(spack_num) == '0'
#                             else str(spack_num))
#     return samples_pack_dirname
