import os

from pathlib import Path
from sys import platform
from renardo.sc_backend.template_renderer import SCTemplateRenderer

SC_USER_CONFIG_DIR = None

# default config path
# on windows AppData/Roaming/renardo
# on Linux ~/.config/renardo
# on MacOS /Users/<username>/Library/Application Support/renardo
if platform == "linux" or platform == "linux2" :
    home_path = Path.home()
    SC_USER_CONFIG_DIR = home_path / '.local' / 'share' / 'SuperCollider'
elif platform == "darwin":
    home_path = Path.home()
    SC_USER_CONFIG_DIR = home_path / 'Library' / 'Application Support' / 'SuperCollider'
elif platform == "win32":
    appdata_local_path = Path(os.getenv('LOCALAPPDATA'))
    SC_USER_CONFIG_DIR = appdata_local_path / 'SuperCollider'

SC_USER_EXTENSIONS_DIR = SC_USER_CONFIG_DIR / 'Extensions'

SCLANG_PROCESS = None

def is_renardo_sc_classes_initialized():
    """Check if SuperCollider classes are initialized and up to date"""
    files_exist = (
        (SC_USER_EXTENSIONS_DIR / 'Renardo.sc').exists()
        and (SC_USER_EXTENSIONS_DIR / 'StageLimiter.sc').exists()
        and (SC_USER_CONFIG_DIR / 'start_renardo.scd').exists()
    )
    
    # If files don't exist, they're not initialized
    if not files_exist:
        return False
    
    # If files exist but are outdated, they need to be reinitialized
    return not should_update_renardo_sc_classes()

def _generate_renardo_sc_class_content():
    """Generate the current expected content for Renardo.sc file using Jinja2 template."""
    renderer = SCTemplateRenderer()
    return renderer.render_renardo_class()

def should_update_renardo_sc_classes():
    """Check if the SuperCollider class files need to be updated"""
    renardo_file = SC_USER_EXTENSIONS_DIR / 'Renardo.sc'
    stagelimiter_file = SC_USER_EXTENSIONS_DIR / 'StageLimiter.sc'
    start_file = SC_USER_CONFIG_DIR / 'start_renardo.scd'
    
    # If any file doesn't exist, we need to create them
    if not (renardo_file.exists() and stagelimiter_file.exists() and start_file.exists()):
        return True
    
    # Check Renardo.sc content
    try:
        with open(renardo_file, 'r') as f:
            current_renardo_content = f.read()
    except (IOError, OSError):
        return True  # If we can't read it, better to regenerate
    
    # Generate expected content for Renardo.sc
    expected_renardo_content = _generate_renardo_sc_class_content()
    
    # Compare Renardo.sc content (normalize whitespace)
    current_renardo_normalized = ' '.join(current_renardo_content.split())
    expected_renardo_normalized = ' '.join(expected_renardo_content.split())
    
    if current_renardo_normalized != expected_renardo_normalized:
        return True
    
    # Check other files exist and have some content (basic check)
    try:
        with open(stagelimiter_file, 'r') as f:
            stagelimiter_content = f.read().strip()
        with open(start_file, 'r') as f:
            start_content = f.read().strip()
        
        # Basic content check - files should not be empty and contain expected keywords
        if (not stagelimiter_content or 'StageLimiterBis' not in stagelimiter_content or
            not start_content or 'Renardo.start' not in start_content):
            return True
            
    except (IOError, OSError):
        return True
    
    return False

def write_sc_renardo_files_in_user_config():
    from renardo.settings_manager import settings

    osc_port = settings.get("sc_backend.PORT")

    # Ensure directories exist
    SC_USER_EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)
    SC_USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize template renderer
    renderer = SCTemplateRenderer()

    # Render templates
    renardo_sc_class = renderer.render_renardo_class()
    stagelimiter_sc_class = renderer.render_stagelimiter_class()

    # Simple startup script (no template needed - too simple)
    renardo_start_code = f'''
        Renardo.start();
        Renardo.midi();
    '''

    # Write files
    with open(SC_USER_EXTENSIONS_DIR / 'StageLimiter.sc', mode="w") as file:
        file.write(stagelimiter_sc_class)

    with open(SC_USER_EXTENSIONS_DIR / 'Renardo.sc', mode="w") as file:
        file.write(renardo_sc_class)

    with open(SC_USER_CONFIG_DIR / 'start_renardo.scd', mode="w") as file:
        file.write(renardo_start_code)
