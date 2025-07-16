#!/usr/bin/env python3
"""Test track items functionality."""

import pytest


def test_track_items_empty(test_track):
    """Test getting items from empty track."""
    items = test_track.items
    assert isinstance(items, list), "Items should be a list"
    assert len(items) == 0, "Empty track should have no items"


def test_add_item_basic(test_track):
    """Test adding basic item to track."""
    initial_items = len(test_track.items)
    
    # Add item
    item = test_track.add_item(position=0.0, length=1.0)
    assert item is not None, "Item should be created"
    
    # Verify item was added
    new_items = len(test_track.items)
    assert new_items == initial_items + 1, "Should have one more item"


def test_add_item_position(test_track):
    """Test adding item with specific position."""
    position = 5.0
    item = test_track.add_item(position=position, length=1.0)
    
    # Verify position was set
    assert abs(item.position - position) < 0.01, f"Item position should be {position}"


def test_add_item_length(test_track):
    """Test adding item with specific length."""
    length = 3.0
    item = test_track.add_item(position=0.0, length=length)
    
    # Verify length was set
    assert abs(item.length - length) < 0.01, f"Item length should be {length}"


def test_add_multiple_items(test_track):
    """Test adding multiple items."""
    initial_count = len(test_track.items)
    
    # Add multiple items
    items = []
    for i in range(3):
        item = test_track.add_item(position=i * 2.0, length=1.5)
        items.append(item)
    
    # Verify all items were added
    final_count = len(test_track.items)
    assert final_count == initial_count + 3, "Should have 3 more items"


def test_get_item_by_index(test_track):
    """Test getting item by index."""
    # Add an item first
    test_track.add_item(position=0.0, length=1.0)
    
    # Get item by index
    item = test_track.get_item(0)
    assert item is not None, "Should be able to get item by index"


def test_get_item_invalid_index(test_track):
    """Test getting item with invalid index."""
    # Try to get item from empty track
    with pytest.raises(ValueError):
        test_track.get_item(0)
    
    # Add an item
    test_track.add_item()
    
    # Try invalid indices
    with pytest.raises(ValueError):
        test_track.get_item(-1)
    
    with pytest.raises(ValueError):
        test_track.get_item(10)


def test_add_midi_item(test_track):
    """Test adding MIDI item to track."""
    initial_items = len(test_track.items)
    
    # Add MIDI item
    item = test_track.add_midi_item(position=0.0, length=2.0)
    assert item is not None, "MIDI item should be created"
    
    # Verify item was added
    new_items = len(test_track.items)
    assert new_items == initial_items + 1, "Should have one more item"


def test_add_midi_item_properties(test_track):
    """Test MIDI item properties."""
    position = 1.0
    length = 4.0
    
    item = test_track.add_midi_item(position=position, length=length)
    
    # Verify properties
    assert abs(item.position - position) < 0.01, f"MIDI item position should be {position}"
    assert abs(item.length - length) < 0.01, f"MIDI item length should be {length}"


def test_item_cache_consistency(test_track):
    """Test that item cache is consistent."""
    # Add items
    test_track.add_item(position=0.0)
    test_track.add_item(position=1.0)
    
    # Get items multiple times
    items1 = test_track.items
    items2 = test_track.items
    
    # Should be the same
    assert len(items1) == len(items2), "Item count should be consistent"
    
    # Get specific item multiple times
    item1 = test_track.get_item(0)
    item2 = test_track.get_item(0)
    
    # Should be the same object (cached)
    assert item1 is item2, "Should return cached item object"


def test_items_after_track_selection(test_track):
    """Test that items work after track operations."""
    # Add item
    test_track.add_item()
    
    # Perform track operations
    test_track.is_selected = True
    test_track.is_muted = True
    test_track.volume = 0.5
    
    # Items should still be accessible
    items = test_track.items
    assert len(items) == 1, "Should still have 1 item after track operations"


def test_item_properties_basic(test_track):
    """Test basic item properties."""
    item = test_track.add_item(position=2.0, length=3.0)
    
    # Test position
    assert hasattr(item, 'position'), "Item should have position property"
    assert isinstance(item.position, (int, float)), "Position should be numeric"
    
    # Test length
    assert hasattr(item, 'length'), "Item should have length property"
    assert isinstance(item.length, (int, float)), "Length should be numeric"


def test_mixed_item_types(test_track):
    """Test mixing different item types."""
    # Add different types of items
    audio_item = test_track.add_item(position=0.0, length=1.0)
    midi_item = test_track.add_midi_item(position=2.0, length=1.0)
    
    # Both should be in items list
    items = test_track.items
    assert len(items) == 2, "Should have 2 items"
    
    # Should be able to get both by index
    item0 = test_track.get_item(0)
    item1 = test_track.get_item(1)
    
    assert item0 is not None, "First item should exist"
    assert item1 is not None, "Second item should exist"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])