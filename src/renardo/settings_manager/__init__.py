from .settings_manager import SettingsManager

from .config_dir import (
    SAMPLES_DIR_PATH, DEFAULT_SAMPLES_PACK_NAME, LOOP_SUBDIR, DESCRIPTIONS,
    SAMPLES_DOWNLOAD_SERVER, get_samples_dir_path, get_user_config_dir_path
)

from .sample_config import nonalpha, alpha

from .supercollider_settings import (
    OSC_MIDI_ADDRESS, GET_SC_INFO, FOXDOT_INFO_FILE, FOXDOT_RECORD_FILE,
    RECORDING_DIR,
)