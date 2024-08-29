// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod get_api_keys;
mod translator_requests;
mod process_call;

use get_api_keys::{get_api_keys, Item};
use translator_requests::*;

#[tauri::command]
fn get_keys() -> Result<Vec<Item>, String> {
    match crate::get_api_keys() {
        Ok(keys) => Ok(keys),
        Err(e) => Err(e.to_string()),
    }
}

// Learn more about Tauri commands at https://tauri.app/v1/guides/features/command

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_keys,check_usage,get_source_languages,get_target_languages,translate_doc_alt,get_glossaries,glossary_from_excel,delete_glossary])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
