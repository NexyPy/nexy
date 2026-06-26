use crate::core::errors::Result;
use crate::core::vfs::Vfs;

pub struct TemplateGenerator;

impl TemplateGenerator {
    pub fn generate(output: &str, template: &str) -> Result<()> {
        Vfs::write(output, template)?;
        Ok(())
    }
}
