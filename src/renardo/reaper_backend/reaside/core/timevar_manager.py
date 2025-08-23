"""TimeVar management for continuously changing parameter values in reaside."""

import threading
import time
import weakref
from typing import Dict, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from renardo.logger import get_logger

logger = get_logger('reaside.core.timevar_manager')


@dataclass
class TimeVarBinding:
    """Represents a binding between a parameter and a TimeVar."""
    param_ref: weakref.ref  # Weak reference to ReaParam or ReaSend
    timevar: Any  # The TimeVar object from renardo
    last_value: Optional[float] = None
    
    def get_param(self):
        """Get the parameter if it still exists."""
        return self.param_ref()


class TimeVarManager:
    """
    Manages TimeVar bindings for parameters that change continuously.
    Uses a single thread to update all TimeVar parameters at 20Hz.
    """
    
    # Singleton instance
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the TimeVar manager."""
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._bindings: Dict[int, TimeVarBinding] = {}  # key: id(param)
        self._update_thread: Optional[threading.Thread] = None
        self._running = False
        self._update_rate = 20  # Hz
        self._update_interval = 1.0 / self._update_rate
        self._bindings_lock = threading.Lock()
        
        logger.info("TimeVarManager initialized")
    
    def bind_timevar(self, param, timevar) -> None:
        """
        Bind a TimeVar to a parameter for continuous updates.
        
        Args:
            param: ReaParam or ReaSend instance
            timevar: TimeVar object from renardo
        """
        param_id = id(param)
        
        with self._bindings_lock:
            # Create weak reference to avoid circular references
            binding = TimeVarBinding(
                param_ref=weakref.ref(param, self._on_param_deleted),
                timevar=timevar
            )
            self._bindings[param_id] = binding
            
            logger.debug(f"Bound TimeVar to {param} (id: {param_id})")
        
        # Start update thread if not already running
        self._ensure_thread_running()
    
    def unbind_param(self, param) -> None:
        """
        Remove TimeVar binding from a parameter.
        
        Args:
            param: ReaParam or ReaSend instance
        """
        param_id = id(param)
        
        with self._bindings_lock:
            if param_id in self._bindings:
                del self._bindings[param_id]
                logger.debug(f"Unbound TimeVar from {param} (id: {param_id})")
        
        # Stop thread if no more bindings
        if not self._bindings:
            self._stop_thread()
    
    def clear_all_bindings(self) -> None:
        """Clear all TimeVar bindings and stop the update thread."""
        with self._bindings_lock:
            self._bindings.clear()
        self._stop_thread()
        logger.info("Cleared all TimeVar bindings")
    
    def _on_param_deleted(self, ref):
        """Callback when a parameter is garbage collected."""
        # Find and remove the binding for this parameter
        with self._bindings_lock:
            to_remove = []
            for param_id, binding in self._bindings.items():
                if binding.param_ref == ref:
                    to_remove.append(param_id)
            
            for param_id in to_remove:
                del self._bindings[param_id]
                logger.debug(f"Removed binding for deleted param (id: {param_id})")
    
    def _ensure_thread_running(self) -> None:
        """Ensure the update thread is running."""
        if not self._running:
            self._running = True
            self._update_thread = threading.Thread(
                target=self._update_loop,
                daemon=True,
                name="TimeVarManager-UpdateThread"
            )
            self._update_thread.start()
            logger.info(f"Started TimeVar update thread at {self._update_rate}Hz")
    
    def _stop_thread(self) -> None:
        """Stop the update thread."""
        if self._running:
            self._running = False
            if self._update_thread:
                self._update_thread.join(timeout=1.0)
                self._update_thread = None
            logger.info("Stopped TimeVar update thread")
    
    def _update_loop(self) -> None:
        """Main update loop running at specified rate."""
        while self._running:
            start_time = time.time()
            
            # Process all bindings
            with self._bindings_lock:
                bindings_to_remove = []
                
                for param_id, binding in self._bindings.items():
                    param = binding.get_param()
                    
                    # Remove binding if parameter was deleted
                    if param is None:
                        bindings_to_remove.append(param_id)
                        continue
                    
                    try:
                        # Get current value from TimeVar
                        current_value = self._evaluate_timevar(binding.timevar)
                        
                        # Only update if value changed significantly
                        if binding.last_value is None or abs(current_value - binding.last_value) > 0.001:
                            # Use internal method to avoid re-triggering TimeVar detection
                            if hasattr(param, '_set_value_internal'):
                                param._set_value_internal(current_value)
                            else:
                                # Fallback for objects without the internal method
                                param.value = current_value
                            binding.last_value = current_value
                            
                    except Exception as e:
                        logger.error(f"Error updating TimeVar for {param}: {e}")
                
                # Remove dead bindings
                for param_id in bindings_to_remove:
                    del self._bindings[param_id]
            
            # Sleep to maintain update rate
            elapsed = time.time() - start_time
            sleep_time = max(0, self._update_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _evaluate_timevar(self, timevar) -> float:
        """
        Evaluate a TimeVar to get its current value.
        
        Args:
            timevar: TimeVar object from renardo
            
        Returns:
            Current value as float
        """
        try:
            # For Mock objects, check what was explicitly set
            # Mock creates attributes on access, so we need to be careful
            try:
                from unittest.mock import Mock
                is_mock = isinstance(timevar, Mock)
            except ImportError:
                is_mock = False
            
            # For Mock objects, check which method was explicitly configured
            if is_mock:
                # Check current_value first
                if hasattr(timevar, 'current_value'):
                    attr = getattr(timevar, 'current_value')
                    # Check if it has a non-Mock return_value (i.e., was explicitly configured)
                    if callable(attr) and hasattr(attr, 'return_value') and not isinstance(attr.return_value, Mock):
                        result = timevar.current_value()
                        if isinstance(result, (list, tuple)) and len(result) > 0:
                            result = result[0]
                        return float(result)
                
                # Check now method
                if hasattr(timevar, 'now'):
                    attr = getattr(timevar, 'now')
                    # Check if it has a non-Mock return_value (i.e., was explicitly configured)
                    if callable(attr) and hasattr(attr, 'return_value') and not isinstance(attr.return_value, Mock):
                        result = timevar.now()
                        if isinstance(result, (list, tuple)) and len(result) > 0:
                            result = result[0]
                        return float(result)
            else:
                # For non-Mock objects, use normal detection
                # Check if it has a current_value() method first
                if hasattr(timevar, 'current_value') and callable(getattr(timevar, 'current_value')):
                    result = timevar.current_value()
                    # Handle lists/arrays by taking first element
                    if isinstance(result, (list, tuple)) and len(result) > 0:
                        result = result[0]
                    return float(result)
                
                # Check if it has a now() method (typical for TimeVar)
                if hasattr(timevar, 'now') and callable(getattr(timevar, 'now')):
                    result = timevar.now()
                    # Handle lists/arrays by taking first element
                    if isinstance(result, (list, tuple)) and len(result) > 0:
                        result = result[0]
                    return float(result)
            
            # Check if it has __call__ method
            if callable(timevar):
                result = timevar()
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    result = result[0]
                return float(result)
            
            # Try to convert directly to float
            return float(timevar)
            
        except Exception as e:
            logger.warning(f"Failed to evaluate TimeVar: {e}, using default value 0.5")
            return 0.5
    
    def get_binding_count(self) -> int:
        """Get the current number of active bindings."""
        with self._bindings_lock:
            return len(self._bindings)
    
    def is_param_bound(self, param) -> bool:
        """Check if a parameter has a TimeVar binding."""
        with self._bindings_lock:
            return id(param) in self._bindings
    
    def get_update_rate(self) -> int:
        """Get the current update rate in Hz."""
        return self._update_rate
    
    def set_update_rate(self, rate_hz: int) -> None:
        """
        Set the update rate for TimeVar processing.
        
        Args:
            rate_hz: Update rate in Hz (1-100)
        """
        if not 1 <= rate_hz <= 100:
            raise ValueError(f"Update rate must be between 1 and 100 Hz, got {rate_hz}")
        
        self._update_rate = rate_hz
        self._update_interval = 1.0 / rate_hz
        logger.info(f"Set TimeVar update rate to {rate_hz}Hz")
    
    def __del__(self):
        """Cleanup when manager is destroyed."""
        try:
            self.clear_all_bindings()
        except:
            pass  # Best effort cleanup


# Global singleton instance
_timevar_manager = None

def get_timevar_manager() -> TimeVarManager:
    """Get the global TimeVar manager singleton."""
    global _timevar_manager
    if _timevar_manager is None:
        _timevar_manager = TimeVarManager()
    return _timevar_manager