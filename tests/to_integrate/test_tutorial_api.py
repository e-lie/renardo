import pytest
from pathlib import Path

def test_tutorial_structure():
    """Test that tutorial structure is correct"""
    tutorial_path = Path(__file__).parent.parent / "src" / "renardo" / "tutorial"
    
    # Check that tutorial directory exists
    assert tutorial_path.exists()
    
    # Check that language directories exist
    en_path = tutorial_path / "en"
    es_path = tutorial_path / "es"
    
    assert en_path.exists()
    assert es_path.exists()
    
    # Check that tutorial files exist
    en_files = list(en_path.glob("*.py"))
    es_files = list(es_path.glob("*.py"))
    
    assert len(en_files) > 0
    assert len(es_files) > 0
    
    # Check that file names match between languages
    en_names = {f.name for f in en_files}
    es_names = {f.name for f in es_files}
    
    # Should have the same files in both languages
    assert en_names == es_names