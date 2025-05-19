"""
Renardo tutorial module

This module provides access to tutorial files in multiple languages.
"""

from pathlib import Path

def get_tutorial_path(language='en'):
    """Get the path to tutorial files for a specific language"""
    tutorial_base = Path(__file__).parent
    lang_path = tutorial_base / language
    
    if lang_path.exists():
        return lang_path
    else:
        # Default to English if language not found
        return tutorial_base / 'en'

def get_available_languages():
    """Get list of available tutorial languages"""
    tutorial_base = Path(__file__).parent
    languages = []
    
    for path in tutorial_base.iterdir():
        if path.is_dir() and not path.name.startswith('_'):
            languages.append(path.name)
    
    return sorted(languages)

# Backward compatibility - if old demo imports exist
def get_demo_files():
    """Deprecated: Use get_tutorial_path('en') instead"""
    import warnings
    warnings.warn(
        "get_demo_files() is deprecated. Use get_tutorial_path('en') instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return list(get_tutorial_path('en').glob('*.py'))