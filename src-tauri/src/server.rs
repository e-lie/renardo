use std::io::{Read, Write};
use std::net::{Ipv4Addr, TcpListener, TcpStream};
use std::path::Path;
use std::process::{Child, Command};
use std::time::{Duration, Instant};

pub struct Server {
    child: Child,
    pub port: u16,
}

fn free_port() -> Result<u16, String> {
    let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0)).map_err(|e| e.to_string())?;
    Ok(listener.local_addr().map_err(|e| e.to_string())?.port())
}

impl Server {
    /// Start the uvicorn server on 127.0.0.1 with a free port.
    /// Release builds use the embedded Python from the bundle resources,
    /// debug builds run from the source tree with `uv`.
    pub fn spawn(resource_dir: &Path, data_dir: &Path) -> Result<Server, String> {
        let port = free_port()?;
        let mut cmd;
        if cfg!(debug_assertions) {
            let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
            cmd = Command::new("uv");
            cmd.args(["run", "uvicorn"]).current_dir(root);
        } else {
            let python = resource_dir.join("python");
            let exe = if cfg!(windows) {
                python.join("python.exe")
            } else {
                python.join("bin").join("python3")
            };
            cmd = Command::new(exe);
            cmd.args(["-m", "uvicorn"]);
            cmd.env("PYTHONNOUSERSITE", "1");
        }
        cmd.args([
            "renardo.webserver.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            &port.to_string(),
        ]);
        cmd.env("RENARDO_USER_DIR", data_dir);

        #[cfg(unix)]
        {
            use std::os::unix::process::CommandExt;
            cmd.process_group(0);
        }
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
        }

        let child = cmd.spawn().map_err(|e| format!("cannot start server: {e}"))?;
        Ok(Server { child, port })
    }

    /// Exit status if the server process has died on its own.
    pub fn exited(&mut self) -> Option<std::process::ExitStatus> {
        self.child.try_wait().ok().flatten()
    }

    /// Kill the server and all its descendants (scsynth, sclang...).
    pub fn stop(&mut self) {
        let pid = self.child.id();
        #[cfg(unix)]
        unsafe {
            // child is its own process group leader: signal the whole group
            libc::killpg(pid as i32, libc::SIGTERM);
        }
        #[cfg(windows)]
        {
            let _ = Command::new("taskkill")
                .args(["/PID", &pid.to_string(), "/T", "/F"])
                .output();
        }
        let deadline = Instant::now() + Duration::from_secs(5);
        while Instant::now() < deadline {
            if let Ok(Some(_)) = self.child.try_wait() {
                break;
            }
            std::thread::sleep(Duration::from_millis(100));
        }
        #[cfg(unix)]
        unsafe {
            libc::killpg(pid as i32, libc::SIGKILL);
        }
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn health_ok(port: u16) -> bool {
    let Ok(mut s) = TcpStream::connect_timeout(
        &(Ipv4Addr::LOCALHOST, port).into(),
        Duration::from_secs(1),
    ) else {
        return false;
    };
    let _ = s.set_read_timeout(Some(Duration::from_secs(2)));
    let req = format!("GET /health HTTP/1.0\r\nHost: 127.0.0.1:{port}\r\n\r\n");
    if s.write_all(req.as_bytes()).is_err() {
        return false;
    }
    let mut buf = String::new();
    let _ = s.read_to_string(&mut buf);
    buf.starts_with("HTTP/1.1 200") || buf.starts_with("HTTP/1.0 200")
}

pub fn wait_healthy(port: u16, timeout: Duration) -> Result<(), String> {
    let deadline = Instant::now() + timeout;
    while Instant::now() < deadline {
        if health_ok(port) {
            return Ok(());
        }
        std::thread::sleep(Duration::from_millis(200));
    }
    Err(format!("server did not answer /health on port {port}"))
}
