// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod get_api_keys;
mod process_call;
mod documents;
mod glossary;
mod translate;
mod utils;

use documents::documents_handler;
use glossary::glossary_handler;
use utils::utils_handler;
use translate::translate_handler;
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
        .invoke_handler(tauri::generate_handler![
            documents_handler::load_document,
            glossary_handler::get_glossaries,
            utils_handler::get_gpt_models,
            utils_handler::get_source_languages,
            utils_handler::get_target_languages,
            utils_handler::check_usage,
            translate_handler::translate_document,
            get_chatgpt_keys,
            get_deep_keys
            ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
