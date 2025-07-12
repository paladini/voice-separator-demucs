// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Command, Stdio};
use std::thread;
use std::time::Duration;

fn start_python_backend() {
    thread::spawn(|| {
        println!("🐍 Starting Python backend...");
        
        // Wait a moment for the main window to be ready
        thread::sleep(Duration::from_secs(2));
        
        // Try multiple Python commands
        let python_commands = if cfg!(target_os = "windows") {
            vec!["python", "py", "python3"]
        } else {
            vec!["python3", "python"]
        };
        
        for python_cmd in python_commands {
            println!("🔄 Trying {} desktop_app.py", python_cmd);
            
            match Command::new(python_cmd)
                .arg("desktop_app.py")
                .current_dir("../")
                .stdout(Stdio::inherit())
                .stderr(Stdio::inherit())
                .spawn()
            {
                Ok(mut child) => {
                    println!("✅ Python backend started with {}", python_cmd);
                    
                    // Wait for the process and keep it running
                    match child.wait() {
                        Ok(status) => {
                            println!("🔄 Python process ended: {}", status);
                        }
                        Err(e) => {
                            println!("❌ Error waiting for Python process: {}", e);
                        }
                    }
                    return; // Exit after first successful start
                }
                Err(e) => {
                    println!("❌ Failed to start with {}: {}", python_cmd, e);
                }
            }
        }
        
        println!("❌ Could not start Python backend with any command");
        println!("💡 Please start manually:");
        println!("   cd /home/paladini/code/pessoal/voice-separator-demucs");
        println!("   python desktop_app.py");
    });
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|_app| {
            println!("� Starting Voice Separator...");
            
            // Start Python backend
            start_python_backend();
            
            Ok(())
        })
        .on_window_event(|_window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                // Just hide the window instead of closing the app completely
                _window.hide().unwrap();
                api.prevent_close();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn main() {
    run();
}
