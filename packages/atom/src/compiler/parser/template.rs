use crate::core::errors::Result;

pub struct TemplateParser;

impl TemplateParser {
    pub fn parse(template: &str) -> Result<String> {
        Ok(template.to_string())
    }
}
