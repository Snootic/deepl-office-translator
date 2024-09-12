use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::BufReader;

#[derive(Deserialize, Serialize, Debug)]
pub struct Item {
    pub key: String,
}

pub fn get_deepl_keys() -> Result<Vec<Item>, Box<dyn std::error::Error>> {
    let file = File::open("../src/config_files/deepl_keys.json")?;
    let reader = BufReader::new(file);

    let items: Vec<Item> = serde_json::from_reader(reader)?;

    Ok(items)
}


pub fn get_gpt_keys() -> Result<Vec<Item>, Box<dyn std::error::Error>> {
    let file = File::open("../src/config_files/gpt_keys.json")?;
    let reader = BufReader::new(file);

    let items: Vec<Item> = serde_json::from_reader(reader)?;

    Ok(items)
}