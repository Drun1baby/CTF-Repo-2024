#[macro_use] extern crate rocket;

use std::fs;
use std::fs::File;
use std::io::Write;
use std::process::Command;
use rand::Rng;

#[get("/")]
fn index() -> String {
    fs::read_to_string("main.rs").unwrap_or(String::default())
}

#[post("/rust_code", data = "<code>")]
fn run_rust_code(code: String) -> String{
    if code.contains("std") {
        return "Error: std is not allowed".to_string();
    }
    //generate a random 5 length file name
    let file_name = rand::thread_rng()
        .sample_iter(&rand::distributions::Alphanumeric)
        .take(5)
        .map(char::from)
        .collect::<String>();
    if let Ok(mut file) = File::create(format!("playground/{}.rs", &file_name)) {
        file.write_all(code.as_bytes());
    }
    if let Ok(build_output) = Command::new("rustc")
        .arg(format!("playground/{}.rs",&file_name))
        .arg("-C")
        .arg("debuginfo=0")
        .arg("-C")
        .arg("opt-level=3")
        .arg("-o")
        .arg(format!("playground/{}",&file_name))
        .output() {
        if !build_output.status.success(){
            fs::remove_file(format!("playground/{}.rs",&file_name));
            return String::from_utf8_lossy(build_output.stderr.as_slice()).to_string();
        }
    }
    fs::remove_file(format!("playground/{}.rs",&file_name));
    if let Ok(output) = Command::new(format!("playground/{}",&file_name))
        .output() {
        if !output.status.success(){
            fs::remove_file(format!("playground/{}",&file_name));
            return String::from_utf8_lossy(output.stderr.as_slice()).to_string();
        } else{
            fs::remove_file(format!("playground/{}",&file_name));
            return String::from_utf8_lossy(output.stdout.as_slice()).to_string();
        }
    }
    return String::default();

}

#[launch]
fn rocket() -> _ {
    let figment = rocket::Config::figment()
        .merge(("address", "0.0.0.0"));
    rocket::custom(figment).mount("/", routes![index,run_rust_code])
}