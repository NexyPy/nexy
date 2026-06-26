use clap::Args;

#[derive(Args)]
pub struct DevArgs {
    #[arg(short, long, default_value = "3000")]
    pub port: u16,

    #[arg(short, long, default_value = "0.0.0.0")]
    pub host: String,
}

pub fn run(args: DevArgs) {
    println!("🧪 Nexy dev server starting on {}:{}", args.host, args.port);
    println!("   (Rust nexy-atom dev mode)");
}
