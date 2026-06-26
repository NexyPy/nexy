pub mod dev;
pub mod build;
pub mod start;
pub mod init;
pub mod new;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "nx", version = "2.0.9", about = "Nexy application server & compiler")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    Dev(dev::DevArgs),
    Build(build::BuildArgs),
    Start(start::StartArgs),
    Init(init::InitArgs),
    New(new::NewArgs),
}

pub fn run() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Dev(args) => dev::run(args),
        Commands::Build(args) => build::run(args),
        Commands::Start(args) => start::run(args),
        Commands::Init(args) => init::run(args),
        Commands::New(args) => new::run(args),
    }
}
