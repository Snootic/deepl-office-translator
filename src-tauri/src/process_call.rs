use std::process::{ Command, Output };

pub fn command(file: &str, key: &str, method: &str, args: Option<&str>) -> Output {
    let mut command = Command::new(file);
    command.arg(format!("key={}",key));
    command.arg(format!("method={}",method));

    if let Some(args) = args {
        command.arg(format!("args={}",args));
    }

    let output = command.output().expect("Failed to execute command");

    output
}
    