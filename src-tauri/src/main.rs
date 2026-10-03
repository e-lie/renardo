#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod server;

use std::sync::Mutex;
use tauri::{Manager, RunEvent, WebviewUrl, WebviewWindowBuilder};
use tauri_plugin_dialog::{DialogExt, MessageDialogKind};

struct ServerState(Mutex<Option<server::Server>>);

fn main() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let handle = app.handle().clone();
            #[cfg(unix)]
            watch_signals(handle.clone());
            std::thread::spawn(move || {
                if let Err(e) = start(&handle) {
                    eprintln!("renardo: failed to start: {e}");
                    handle.exit(1);
                }
            });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|handle, event| {
        if let RunEvent::Exit = event {
            if let Some(state) = handle.try_state::<ServerState>() {
                if let Some(mut srv) = state.0.lock().unwrap().take() {
                    srv.stop();
                }
            }
        }
    });
}

/// SIGTERM/SIGINT/SIGHUP skip the Exit event: stop the server tree explicitly.
#[cfg(unix)]
fn watch_signals(handle: tauri::AppHandle) {
    use signal_hook::consts::{SIGHUP, SIGINT, SIGTERM};
    let Ok(mut signals) = signal_hook::iterator::Signals::new([SIGTERM, SIGINT, SIGHUP]) else {
        return;
    };
    std::thread::spawn(move || {
        if signals.forever().next().is_some() {
            handle.exit(0);
        }
    });
}

/// Report an unexpected server exit to the user, then quit.
fn watch_server(handle: tauri::AppHandle) {
    std::thread::spawn(move || loop {
        std::thread::sleep(std::time::Duration::from_millis(500));
        let Some(state) = handle.try_state::<ServerState>() else {
            return;
        };
        let status = match state.0.lock().unwrap().as_mut() {
            Some(srv) => srv.exited(),
            None => return, // server already stopped on purpose
        };
        if let Some(status) = status {
            eprintln!("renardo: server exited unexpectedly ({status})");
            let h = handle.clone();
            handle
                .dialog()
                .message(format!(
                    "The Renardo server stopped unexpectedly ({status}). The application will close."
                ))
                .title("Renardo")
                .kind(MessageDialogKind::Error)
                .show(move |_| h.exit(1));
            return;
        }
    });
}

fn start(handle: &tauri::AppHandle) -> Result<(), String> {
    let data_dir = handle.path().app_data_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&data_dir).map_err(|e| e.to_string())?;
    let resource_dir = handle.path().resource_dir().map_err(|e| e.to_string())?;

    let srv = server::Server::spawn(&resource_dir, &data_dir)?;
    let port = srv.port;
    handle.manage(ServerState(Mutex::new(Some(srv))));

    watch_server(handle.clone());
    server::wait_healthy(port, std::time::Duration::from_secs(60))?;

    let url = format!("http://127.0.0.1:{port}");
    WebviewWindowBuilder::new(
        handle,
        "main",
        WebviewUrl::External(url.parse().map_err(|e| format!("{e}"))?),
    )
    .title("Renardo")
    .inner_size(1400.0, 900.0)
    .build()
    .map_err(|e| e.to_string())?;
    Ok(())
}
