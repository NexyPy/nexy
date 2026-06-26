use std::path::{Path, PathBuf};
use crate::core::config::NexyConfig;
use crate::core::errors::Result;

pub struct Discovery;

impl Discovery {
    pub fn scan(root_dir: &Path) -> Result<Vec<PathBuf>> {
        let mut files = Vec::new();

        let walker = walkdir::WalkDir::new(root_dir)
            .into_iter()
            .filter_entry(|e| {
                let name = e.file_name().to_string_lossy();
                let path = e.path().to_string_lossy().to_lowercase();

                !name.starts_with('.')
                    && !path.contains("__pycache__")
                    && !path.contains(".git")
                    && !path.contains(".venv")
                    && !path.contains("node_modules")
                    && !path.contains("dist")
                    && !path.contains("build")
                    && !path.contains("__nexy__")
            });

        for entry in walker.filter_map(|e| e.ok()) {
            if !entry.file_type().is_file() {
                continue;
            }

            let path = entry.path();
            if NexyConfig::is_nexy_file(path) || NexyConfig::is_mdx_file(path) {
                files.push(path.to_path_buf());
            }
        }

        Ok(files)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_discovery() {
        let dir = std::env::temp_dir().join("nexy_discovery_test");
        let _ = fs::create_dir_all(&dir);
        fs::write(dir.join("index.nexy"), "---\n---\n<div/>").unwrap();
        fs::write(dir.join("about.nexy"), "---\n---\n<div/>").unwrap();
        fs::write(dir.join("readme.md"), "# Hello").unwrap();

        let files = Discovery::scan(&dir).unwrap();
        assert_eq!(files.len(), 2);

        let _ = fs::remove_dir_all(&dir);
    }
}
