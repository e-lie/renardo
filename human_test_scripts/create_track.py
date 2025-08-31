

from renardo.reaper_backend.reaside.tools.rust_osc_client import get_rust_osc_client

rust_client = get_rust_osc_client()

test_value = 6113

track_index = rust_client.add_track(
    position=-1,
    name=f"Test {test_value}",
    input_value=test_value,
    record_armed=False,
    record_mode=2,
    timeout=2.0
)