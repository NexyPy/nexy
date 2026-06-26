pub mod fbrouter;
pub mod discovery;
pub mod layout;
pub mod actions;

use std::path::PathBuf;
use crate::core::errors::Result;
use crate::core::models::Route;
use fbrouter::FbRouter;

pub enum RouterType {
    FileBased(FbRouter),
    Modular,
}

pub struct Router {
    inner: RouterType,
}

impl Router {
    pub fn new_file_based(routes_dir: PathBuf) -> Self {
        Self {
            inner: RouterType::FileBased(FbRouter::new(routes_dir)),
        }
    }

    pub fn new_modular() -> Self {
        Self {
            inner: RouterType::Modular,
        }
    }

    pub fn discover(&self) -> Result<Vec<Route>> {
        match &self.inner {
            RouterType::FileBased(r) => r.discover(),
            RouterType::Modular => Ok(Vec::new()),
        }
    }
}
