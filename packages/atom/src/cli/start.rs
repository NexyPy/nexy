use clap::Args;

#[derive(Args)]
pub struct StartArgs {
    #[arg(short, long, default_value = "3000")]
    pub port: u16,

    #[arg(short, long, default_value = "0.0.0.0")]
    pub host: String,
}

pub fn run(args: StartArgs) {
    println!("🚀 Nexy production server on {}:{}", args.host, args.port);
}
