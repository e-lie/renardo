from datetime import datetime
from pathlib import Path

from renardo.settings_manager import settings
from renardo.gatherer.collection_download import download_files_from_json_index_concurrent

def is_default_sccode_pack_initialized():
    return (settings.get_path("SCCODE_LIBRARY") / settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME") / 'downloaded_at.txt').exists()





def download_default_sccode_pack_and_special(logger=None):

    logger.write_line(
        "Downloading core sccode from {}\n".format(
            settings.get("core.COLLECTIONS_DOWNLOAD_SERVER")
        )
    )
    download_files_from_json_index_concurrent(
        json_url='{}/{}/collection_index.json'.format(
            settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
            settings.get("sc_backend.SPECIAL_SCCODE_DIR_NAME"),
        ),
        download_dir=settings.get_path("SPECIAL_SCCODE_DIR").parent,
        logger=logger
    )

    logger.write_line(
        "Downloading Default Instruments and Effects Pack {} from {}\n".format(
            settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME"),
            settings.get("core.COLLECTIONS_DOWNLOAD_SERVER")
        )
    )
    download_files_from_json_index_concurrent(
        json_url='{}/{}/{}/collection_index.json'.format(
            settings.get("core.COLLECTIONS_DOWNLOAD_SERVER"),
            settings.get("sc_backend.SCCODE_LIBRARY_DIR_NAME"),
            settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME")
        ),
        download_dir=settings.get_path("SCCODE_LIBRARY"),
        logger=logger
    )

    # create a downloaded_at file
    try:
        with open(
                settings.get_path("SCCODE_LIBRARY") / settings.get("sc_backend.DEFAULT_SCCODE_PACK_NAME") / 'downloaded_at.txt',
                mode="w"
        ) as file:
            file.write(str(datetime.now()))

    except Exception as e:
        print(e)

