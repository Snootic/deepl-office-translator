use core::str;
use serde::Serialize;

use crate::process_call;
use process_call::command;

use tauri::api::path::document_dir;
use std::fs::File;
use std::io::Write;

#[cfg(target_os = "windows")]
const SYSTEM: &str = "exe";

#[cfg(not(target_os = "windows"))]
const SYSTEM: &str = "bin";

#[derive(Serialize)]
struct Results {
    success: bool,
    output: Option<serde_json::Value>,
    error: Option<String>,
}

fn generic_request(file: &str, key: &str, method: &str, args: Option<&str>, tool: Option<&str>) -> Result<String, String>{
    let file_with_ext = format!("{}{}", file, SYSTEM);
    let output = command(&file_with_ext, key, method, args, tool);

    let result = if output.status.success() {
        let stdout = str::from_utf8(&output.stdout).map_err(|e| e.to_string())?;
        match serde_json::from_str(stdout) {
            Ok(parsed_output) => Results {
                success: true,
                output: Some(parsed_output),
                error: None,
            },
            Err(e) => Results {
                success: false,
                output: None,
                error: Some(format!("Request failed: {}", e)),
            },
        }
    } else {
        let stderr = str::from_utf8(&output.stderr).map_err(|e| e.to_string())?;
        Results {
            success: false,
            output: None,
            error: Some(stderr.to_string()),
        }
    };

    serde_json::to_string(&result).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn check_usage(key: &str) -> Result<String, String> {
    generic_request("../src/translator/utils.", key, "check_usage", None, Some("deepl"))
}

#[tauri::command]
pub fn get_source_languages(key: &str) -> Result<String, String> {
    generic_request("../src/translator/utils.", key, "get_languages", Some("source"), Some("deepl"))
}

#[tauri::command]
pub fn get_target_languages(key: &str) -> Result<String, String> {
    generic_request("../src/translator/utils.", key, "get_languages", Some("target"), Some("deepl"))
}

#[tauri::command]
pub fn glossary_from_excel(key: &str, args: &str) -> Result<String, String> {
    generic_request("../src/translator/glossary.", key, "create_from_excel", Some(args), None)
}

#[tauri::command]
pub fn get_glossaries(key: &str) -> Result<String, String> {
    generic_request("../src/translator/glossary.", key, "get_glossaries", None, None)
}

#[tauri::command]
pub fn delete_glossary(key: &str, glossary_id: &str) -> Result<String, String> {
    generic_request("../src/translator/glossary.", key, "delete_glossary", Some(glossary_id), None)
}

#[tauri::command]
pub fn get_glossaries_entries(key: &str) -> Result<String, String> {
    generic_request("../src/translator/glossary.", key, "get_glossaries_entries", None, None)
}

#[tauri::command]
pub fn translate_document(key: &str, args: &str) -> Result<String, String> {
    generic_request("../src/translator/translate.", key, "translate_doc", Some(args), None)
}

#[tauri::command]
pub fn translate_doc_alt(key: &str, file_data: Vec<u8>, file_name: &str, file_output: &str, source_language: &str, target_language: &str, glossary_id: Option<&str>) -> Result<String, String> {
    let file_relative_path = format!(".{}", file_name);

    let mut file = File::create(&file_relative_path).map_err(|e| e.to_string())?;
    file.write_all(&file_data).map_err(|e| e.to_string())?;

    let file_path = std::path::PathBuf::from(&file_relative_path);
    let file_abs_path = std::fs::canonicalize(file_path).map_err(|e| e.to_string())?;

    let args = format!("{},{},{},{},{}",file_abs_path.display(),file_output,target_language,source_language,glossary_id.unwrap_or("None"));
    
    generic_request("../src/translator/translate.", key, "translate_word_preserve_format", Some(&args), None)
}

#[tauri::command]
pub fn translate_excel_alt(key: &str, args: &str) -> Result<String, String> {
    generic_request("../src/translator/translate.", key, "translate_excel", Some(args), None)
}

#[tauri::command]
pub fn get_gpt_models(key: &str, args: &str) -> Result<String, String> {
    generic_request("../src/translator/utils.", key, "translate_excel", Some(args), Some("gpt"))
}
