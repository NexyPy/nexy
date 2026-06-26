use std::path::PathBuf;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum NexyError {
    #[error("File not found: {0}")]
    FileNotFound(PathBuf),

    #[error("Compile error in {path} — {message}")]
    CompileError {
        path: PathBuf,
        message: String,
        line: Option<usize>,
        column: Option<usize>,
    },

    #[error("Parse error: {0}")]
    ParseError(String),

    #[error("Config error: {0}")]
    ConfigError(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Router error: {0}")]
    RouterError(String),

    #[error("Build error: {0}")]
    BuildError(String),

    #[error("VFS error: {0}")]
    VfsError(String),

    #[error("{0}")]
    Custom(String),
}

pub type Result<T> = std::result::Result<T, NexyError>;

impl NexyError {
    pub fn compile(path: PathBuf, message: impl Into<String>) -> Self {
        Self::CompileError {
            path,
            message: message.into(),
            line: None,
            column: None,
        }
    }

    pub fn parse(message: impl Into<String>) -> Self {
        Self::ParseError(message.into())
    }
}
