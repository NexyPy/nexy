use clap::Args;

#[derive(Args)]
pub struct InitArgs;

pub fn run(_args: InitArgs) {
    println!("📦 Initializing Nexy project...");
}
