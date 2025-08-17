# Renardo Logger Usage

Renardo provides a centralized logging system that offers consistent formatting, colors, and module-specific logging across all components.

## Basic Usage

### In any module

```python
from renardo.logger import get_logger

# Get a logger for your module
logger = get_logger('my_module')

# Use it
logger.info("Module initialized")
logger.warning("Something might be wrong")
logger.error("An error occurred")
logger.debug("Debug information")  # Only shown in debug mode
```

### Module naming convention

Use hierarchical names that reflect your module structure:

```python
# For a module at src/renardo/some_component/core/feature.py
logger = get_logger('some_component.core.feature')

# For reaside modules
logger = get_logger('reaside.core.project')
logger = get_logger('reaside.tools.http_client')

# For general modules
logger = get_logger('foxdot_editor')
logger = get_logger('sc_backend')
```

## Configuration

### Global configuration

```python
from renardo.logger import configure_logging
import logging

# Configure for development (with colors and debug)
configure_logging(
    level=logging.DEBUG,
    use_colors=True,
    show_module=True,
    log_file=None
)

# Configure for production (minimal output)
configure_logging(
    level=logging.WARNING,
    use_colors=False,
    show_module=False,
    log_file=Path("renardo.log")
)
```

### Per-module configuration

```python
from renardo.logger import set_log_level, enable_debug, disable_debug
import logging

# Set specific level for a module
set_log_level(logging.DEBUG, 'reaside')        # Debug only for reaside
set_log_level(logging.WARNING, 'sc_backend')   # Only warnings for SC backend

# Quick debug enable/disable
enable_debug('reaside.core.timevar_manager')   # Debug for TimeVar manager
disable_debug('reaside')                       # Disable debug for all reaside
```

## Output Examples

With colors and module names enabled:

```
[renardo.reaside.core.project] INFO: Project initialized
[renardo.reaside.core.timevar_manager] WARNING: TimeVar evaluation failed
[renardo.sc_backend] ERROR: SuperCollider connection lost
[renardo.foxdot_editor] DEBUG: Syntax highlighting updated
```

## Integration with existing code

### Migrating from standard logging

**Before:**
```python
import logging
logger = logging.getLogger(__name__)
```

**After:**
```python
from renardo.logger import get_logger
logger = get_logger('my_module.specific_name')
```

### In reaside (already migrated)

All reaside modules now use the renardo logger:
- `reaside.core.project`
- `reaside.core.timevar_manager`  
- `reaside.tools.reaper_http_client`
- etc.

## Advanced Features

### List all active loggers

```python
from renardo.logger import list_loggers

loggers = list_loggers()
for name, level in loggers.items():
    print(f"{name}: {level}")
```

### Custom formatting

The logger automatically provides:
- **Colors**: Different colors for each log level
- **Module prefixes**: `[module.name]` prefix for each message
- **Consistent formatting**: Standardized across all renardo components

### File logging

```python
from pathlib import Path
from renardo.logger import configure_logging

# Log to file as well as console
configure_logging(log_file=Path("renardo_debug.log"))
```

## Best Practices

1. **Use hierarchical names**: `component.submodule.feature`
2. **Be descriptive**: Include context in log messages
3. **Use appropriate levels**:
   - `DEBUG`: Detailed debugging information
   - `INFO`: General information about program execution
   - `WARNING`: Something unexpected happened but program continues
   - `ERROR`: Serious problem occurred
   - `CRITICAL`: Very serious error occurred

4. **Don't log sensitive information**: Avoid passwords, tokens, etc.

Example of good logging:

```python
logger = get_logger('reaside.core.timevar_manager')

logger.info("TimeVarManager initialized")
logger.debug(f"Binding TimeVar to parameter {param.name}")
logger.warning(f"Failed to evaluate TimeVar: {e}, using default value")
logger.error(f"Critical error in update loop: {e}")
```