# Reaside Test Suite

This directory contains comprehensive tests for the reaside module, organized into focused test files.

## Test Structure

### Core Files
- `conftest.py` - Shared fixtures and test configuration

### Test Categories

#### 1. REAPER Startup and Connection (`test_reaper_startup.py`)
- Tests REAPER process startup
- Client connection and reconnection
- Version information retrieval
- Main window accessibility

#### 2. Project Management (`test_project_management.py`)
- Project name getting/setting
- Track count retrieval
- Master track access

#### 3. Basic Track Operations (`test_track_basic.py`)
- Track creation and deletion
- Track name operations
- Track selection, mute, solo states
- Track volume and pan controls

#### 4. Basic FX Operations (`test_fx_basic.py`)
- Adding single and multiple FX
- FX count and name retrieval
- FX enabled state checking

#### 5. FX Objects (`test_fx_objects.py`)
- ReaFX object creation
- Parameter management
- FX enable/disable operations

#### 6. FX Chains (`test_fx_chains.py`)
- FX chain save/load functionality
- Basic file handling

## Key Fixtures

### Session-scoped Fixtures
- `reaper_session` - Single REAPER instance for all tests
- `client` - Connected REAPER client
- `project` - Current project instance

### Test-scoped Fixtures
- `clean_project` - Project with only master track
- `test_track` - Clean track for testing
- `test_track_with_fx` - Track with ReaEQ FX loaded
- `temp_dir` - Temporary directory for test files
- `fx_chain_file` - Temporary FX chain file path
- `reafx_instance` - ReaFX object for testing

## Running Tests

### Run All Tests
```bash
# From project root
uv run pytest tests/reaside/ -v

# Or from the test directory
cd tests/reaside
uv run pytest -v
```

### Run Specific Test Files
```bash
# Individual test files
uv run pytest tests/reaside/test_reaper_startup.py -v
uv run pytest tests/reaside/test_fx_basic.py -v
uv run pytest tests/reaside/test_track_basic.py -v

# Specific test functions
uv run pytest tests/reaside/test_fx_basic.py::test_add_single_fx -v
uv run pytest tests/reaside/test_track_basic.py::test_track_creation -v
```

### Run with Coverage
```bash
uv run pytest --cov=renardo.reaper_backend.reaside tests/reaside/
```

## Test Organization Benefits

1. **Focused Testing** - Each file tests a specific aspect of functionality
2. **Atomic Tests** - Small, single-purpose test functions
3. **Shared Fixtures** - Common setup code reused across tests
4. **Better Debugging** - Easier to isolate and fix specific issues
5. **Parallel Execution** - Tests can be run in parallel for faster execution
6. **Clear Structure** - Easy to understand what each test covers

## Test Naming Convention

- Test files: `test_<category>.py`
- Test functions: `test_<specific_functionality>`
- Fixtures: `<resource_name>` (e.g., `test_track`, `client`)

## Important Notes

- All tests use a single REAPER session to improve performance
- Tests are designed to be independent and can run in any order
- Temporary files are automatically cleaned up after tests
- Tests focus on core functionality without complex edge cases
- Some FX chain functionality is expected to have limited implementation