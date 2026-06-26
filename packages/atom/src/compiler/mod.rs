mod parser;
mod generator;

use std::path::PathBuf;
use crate::core::config::NexyConfig;
use crate::core::errors::{NexyError, Result};

pub use parser::Parser;
pub use generator::Generator;

pub struct Compiler {
    input: PathBuf,
    output: Option<String>,
    parser: Parser,
    generator: Generator,
    source_code: String,
}

impl Compiler {
    pub fn new() -> Self {
        Self {
            input: PathBuf::new(),
            output: None,
            parser: Parser::new(),
            generator: Generator::new(),
            source_code: String::new(),
        }
    }

    pub fn compile(&mut self, input: impl Into<PathBuf>, output: Option<String>) -> Result<()> {
        self.input = input.into();
        self.output = output;
        self.source_code = self.load_source()?;

        let output_path = self.resolve_output()?;

        let parsed = self.parser.process(&self.source_code, &self.input)?;
        self.generator.generate(&output_path, &parsed, &self.input)?;

        Ok(())
    }

    fn load_source(&self) -> Result<String> {
        std::fs::read_to_string(&self.input)
            .map_err(|_e| NexyError::FileNotFound(self.input.clone()))
    }

    fn resolve_output(&self) -> Result<String> {
        if let Some(out) = &self.output {
            return Ok(out.clone());
        }

        let namespace = NexyConfig::global_try().map_or_else(
            || "__nexy__".to_string(),
            |config| config.namespace.trim_end_matches('/').to_string(),
        );

        let file_name = self.input
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("");

        let mapped = if NexyConfig::is_nexy_file(&self.input) {
            file_name.replace(".nexy", ".html")
        } else if NexyConfig::is_mdx_file(&self.input) {
            file_name.replace(".mdx", ".md")
        } else {
            return Err(NexyError::CompileError {
                path: self.input.clone(),
                message: format!("Unsupported file type: {:?}", self.input),
                line: None,
                column: None,
            });
        };

        Ok(format!("{}/{}", namespace, mapped))
    }
}

impl Default for Compiler {
    fn default() -> Self {
        Self::new()
    }
}
