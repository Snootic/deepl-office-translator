pub mod translate_handler {
    use crate::process_call;
    use process_call::handle_python_call;

    #[tauri::command]
    pub async fn translate_document (api_key: &str, model: &str, args: Vec<&str>, kwargs: Option<Vec<(&str, &str)>>) -> Result<String, String> {
        handle_python_call(
            "../src/translator/translate.py", 
            "translate", 
            "translate",
            Some(vec![api_key,model]), 
            "translate_document", 
            Some(args), 
            Some(kwargs.expect("where is the kwargs? kk"))
        ).map_err(|e| e.to_string())
    }
}