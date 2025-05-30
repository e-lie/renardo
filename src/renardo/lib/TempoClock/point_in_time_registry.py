"""
Global registry for managing relationships between PointInTime objects.
This module provides a central mechanism to track dependencies between different
PointInTime instances, allowing for more reliable time-based scheduling.
"""

class PointInTimeRegistry:
    """
    A global registry that tracks relationships between PointInTime objects.
    
    This registry maintains persistent connections between source points and their
    derived points, ensuring that operations like (point + 16) remain connected
    even after the original point has been triggered.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self._registry = {}  # Maps source_id -> {derived_id: (derived_point, operation)}
        self._reverse_lookup = {}  # Maps derived_id -> [source_ids]
    
    def register_derived_point(self, source_point, derived_point, operation=None):
        """
        Register a relationship between a source point and its derived point.
        
        Args:
            source_point: The original PointInTime object
            derived_point: A PointInTime derived from source_point (e.g., source_point + 16)
            operation: Optional operation info (for debugging/introspection)
        """
        source_id = id(source_point)
        derived_id = id(derived_point)
        
        # Create entry for source if it doesn't exist
        if source_id not in self._registry:
            self._registry[source_id] = {}
        
        # Add derived point to source's registry
        self._registry[source_id][derived_id] = (derived_point, operation)
        
        # Update reverse lookup
        if derived_id not in self._reverse_lookup:
            self._reverse_lookup[derived_id] = []
        
        if source_id not in self._reverse_lookup[derived_id]:
            self._reverse_lookup[derived_id].append(source_id)
    
    def get_derived_points(self, source_point):
        """
        Get all points derived from the given source point.
        
        Args:
            source_point: The source PointInTime object
            
        Returns:
            List of (derived_point, operation) tuples
        """
        source_id = id(source_point)
        if source_id in self._registry:
            return list(self._registry[source_id].values())
        return []
    
    def get_source_points(self, derived_point):
        """
        Get all source points that the given derived point depends on.
        
        Args:
            derived_point: The derived PointInTime object
            
        Returns:
            List of source point objects
        """
        derived_id = id(derived_point)
        result = []
        
        if derived_id in self._reverse_lookup:
            for source_id in self._reverse_lookup[derived_id]:
                for registry_dict in self._registry.values():
                    for registered_id, (point, _) in registry_dict.items():
                        if registered_id == source_id:
                            result.append(point)
        
        return result
    
    def notify_derived_points(self, source_point, beat_value):
        """
        Notify all derived points that the source point has been defined with a new beat value.
        Unlike the original implementation, this does NOT clear the derived points after notification.
        
        Args:
            source_point: The source PointInTime that has been updated
            beat_value: The beat value assigned to the source point
            
        Returns:
            Number of derived points notified
        """
        source_id = id(source_point)
        notified_count = 0
        
        if source_id in self._registry:
            for derived_id, (derived_point, _) in list(self._registry[source_id].items()):
                if not derived_point.is_defined:
                    try:
                        # Set the derived point's beat to trigger its operations
                        derived_point.beat = beat_value
                        notified_count += 1
                    except Exception as e:
                        print(f"Error notifying derived PointInTime: {e}")
        
        return notified_count
    
    def clear_derived_points(self, source_point):
        """
        Remove all derived points for a source point.
        
        Args:
            source_point: The source PointInTime to clear derived points for
        """
        source_id = id(source_point)
        
        if source_id in self._registry:
            # Get all derived IDs to update reverse lookup
            derived_ids = list(self._registry[source_id].keys())
            
            # Remove from reverse lookup
            for derived_id in derived_ids:
                if derived_id in self._reverse_lookup:
                    if source_id in self._reverse_lookup[derived_id]:
                        self._reverse_lookup[derived_id].remove(source_id)
                    
                    # Clean up empty entries
                    if not self._reverse_lookup[derived_id]:
                        del self._reverse_lookup[derived_id]
            
            # Clear the registry entry
            del self._registry[source_id]
    
    def clear_all(self):
        """Clear the entire registry."""
        self._registry.clear()
        self._reverse_lookup.clear()
    
    def remove_point(self, point):
        """
        Remove a point from the registry (both as source and derived).
        
        Args:
            point: The PointInTime to remove
        """
        point_id = id(point)
        
        # Remove as source
        if point_id in self._registry:
            self.clear_derived_points(point)
        
        # Remove as derived
        if point_id in self._reverse_lookup:
            source_ids = self._reverse_lookup[point_id].copy()
            for source_id in source_ids:
                if source_id in self._registry and point_id in self._registry[source_id]:
                    del self._registry[source_id][point_id]
                    
                    # Clean up empty entries
                    if not self._registry[source_id]:
                        del self._registry[source_id]
            
            del self._reverse_lookup[point_id]

# Create a global instance
registry = PointInTimeRegistry()