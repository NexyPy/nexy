use clap::Args;

#[derive(Args)]
pub struct BuildArgs {
    #[arg(long)]
    pub check: bool,
}

pub fn run(args: BuildArgs) {
    println!("🔨 Nexy build (check: {})", args.check);
}
