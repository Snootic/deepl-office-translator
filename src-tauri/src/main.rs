// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod get_api_keys;
mod process_call;
mod documents;

use documents::documents_handler;
use get_api_keys::{get_deepl_keys, get_gpt_keys, Item};

#[tauri::command]
fn get_chatgpt_keys() -> Result<Vec<Item>, String> {
    match crate::get_gpt_keys() {
        Ok(keys) => Ok(keys),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
fn get_deep_keys() -> Result<Vec<Item>, String> {
    match crate::get_deepl_keys() {
        Ok(keys) => Ok(keys),
        Err(e) => Err(e.to_string()),
    }
}


// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![documents_handler::load_document])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
