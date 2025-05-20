
# Expose all
# import renardo.gatherer.config_dir
# import renardo.gatherer.collection_download
# from renardo.gatherer.sample_management import sample_file, sample_category, sample_pack, sample_pack_dict, default_samples

# Expose effectively used only

from renardo.gatherer.sample_management import SamplePackLibrary, ensure_renardo_samples_directory
from renardo.gatherer.sample_management.sample_file import SampleFile
from renardo.gatherer.sample_management.default_samples import is_default_spack_initialized, download_default_sample_pack
from renardo.gatherer.sccode_management.default_sccode_pack import (
    is_default_sccode_pack_initialized,
    is_special_sccode_initialized,
    download_special_sccode_pack,
)

from renardo.gatherer.sccode_management import SCResourceLibrary, SCResourceFile, ensure_sccode_directories
from renardo.gatherer.reaper_resource_management import ReaperResourceLibrary, ReaperResourceFile, ensure_reaper_directories

# def main():
    # pass

# def get_spack_dirname_from_num(spack_num):
#     '''associate samples pack directory names in sample folder with pack numbers'''
#     samples_pack_dirname = ('foxdot_default' if str(spack_num) == '0'
#                             else str(spack_num))
#     return samples_pack_dirname
