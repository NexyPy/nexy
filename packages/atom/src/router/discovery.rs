use std::path::PathBuf;
use crate::core::config::NexyConfig;
use crate::core::errors::Result;

pub struct RouteDiscovery;

impl RouteDiscovery {
    pub fn scan(routes_dir: impl Into<PathBuf>) -> Result<Vec<PathBuf>> {
        let config = NexyConfig::global();
        let routes_dir = routes_dir.into();
        let mut files = Vec::new();

        if !routes_dir.exists() {
            return Ok(files);
        }

        let walker = walkdir::WalkDir::new(&routes_dir)
            .into_iter()
            .filter_entry(|e| {
                let name = e.file_name().to_string_lossy();
                !name.starts_with('.')
                    && name != "__pycache__"
                    && name != "node_modules"
            });

        for entry in walker.filter_map(|e| e.ok()) {
            if !entry.file_type().is_file() {
                continue;
            }
            if config.is_route_file(entry.path()) {
                files.push(entry.path().to_path_buf());
            }
        }

        Ok(files)
    }
}
