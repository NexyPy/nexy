mod discovery;

use std::path::Path;
use crate::compiler::Compiler;
use crate::core::errors::Result;
use crate::core::models::BuildResult;
use crate::core::vfs::Vfs;

pub use discovery::Discovery;

pub struct Builder;

impl Builder {
    pub fn new() -> Self {
        Self
    }

    pub fn build(&self, root_dir: &Path) -> Result<BuildResult> {
        Vfs::clear();

        let files = Discovery::scan(root_dir)?;

        if files.is_empty() {
            return Ok(BuildResult {
                success: Vec::new(),
                failed: Vec::new(),
                total: 0,
            });
        }

        let mut success = Vec::new();
        let mut failed = Vec::new();
        let total = files.len();

        for file in &files {
            let mut compiler = Compiler::new();
            match compiler.compile(file, None) {
                Ok(()) => {
                    success.push(file.to_string_lossy().to_string());
                }
                Err(e) => {
                    failed.push((file.to_string_lossy().to_string(), e.to_string()));
                }
            }
        }

        Ok(BuildResult {
            success,
            failed,
            total,
        })
    }
}

impl Default for Builder {
    fn default() -> Self {
        Self::new()
    }
}
