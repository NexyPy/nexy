mod scanner;
mod logic;
mod template;
pub mod validator;

use std::path::Path;
use crate::core::errors::Result;
use crate::core::models::{Component, ParserModel};

pub struct Parser;

impl Parser {
    pub fn new() -> Self {
        Self
    }

    pub fn process(&self, source: &str, file_path: &Path) -> Result<ParserModel> {
        let scan = scanner::Scanner::scan(source)
            .map_err(|e| crate::core::errors::NexyError::parse(e))?;

        let logic = logic::LogicParser::process(&scan.logic_block, file_path)
            .map_err(|e| crate::core::errors::NexyError::parse(e))?;

        validator::ImportValidator::validate(&logic.imports, file_path)?;

        let template = template::TemplateParser::parse(&scan.template_block)?;

        let component = Component {
            name: file_path
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("component")
                .to_string(),
            props: logic.props,
            imports: logic.imports,
            python_code: logic.python_code,
            template,
            source_path: file_path.to_string_lossy().to_string(),
            framework: None,
        };

        Ok(ParserModel {
            component,
            dependencies: logic.dependencies,
            css_imports: logic.css_imports,
            layout: None,
        })
    }
}

impl Default for Parser {
    fn default() -> Self {
        Self::new()
    }
}
