use clap::Args;

#[derive(Args)]
pub struct NewArgs {
    pub name: String,

    #[arg(short, long)]
    pub template: Option<String>,
}

pub fn run(args: NewArgs) {
    println!("✨ Creating new Nexy project: {}", args.name);
}
