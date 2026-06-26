mod logic;
mod template;

use std::path::Path;
use crate::core::errors::Result;
use crate::core::models::ParserModel;

pub use logic::LogicGenerator;
pub use template::TemplateGenerator;

pub struct Generator;

impl Generator {
    pub fn new() -> Self {
        Self
    }

    pub fn generate(
        &self,
        output: &str,
        parsed: &ParserModel,
        _source_path: &Path,
    ) -> Result<()> {
        let _logic_module = LogicGenerator::generate(&parsed.component)?;

        TemplateGenerator::generate(output, &parsed.component.template)?;

        Ok(())
    }
}

impl Default for Generator {
    fn default() -> Self {
        Self::new()
    }
}
