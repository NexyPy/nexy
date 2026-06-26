use std::path::{Path, PathBuf};
use dashmap::DashMap;
use once_cell::sync::Lazy;
use crate::core::errors::{NexyError, Result};

static VFS: Lazy<VirtualFileSystem> = Lazy::new(VirtualFileSystem::new);

pub struct Vfs;

impl Vfs {
    pub fn global() -> &'static VirtualFileSystem {
        &VFS
    }

    pub fn write(path: impl AsRef<Path>, content: impl Into<String>) -> Result<()> {
        VFS.write(path, content)
    }

    pub fn read(path: impl AsRef<Path>) -> Result<String> {
        VFS.read(path)
    }

    pub fn exists(path: impl AsRef<Path>) -> bool {
        VFS.exists(path)
    }

    pub fn delete(path: impl AsRef<Path>) -> Result<()> {
        VFS.delete(path)
    }

    pub fn clear() {
        VFS.clear();
    }

    pub fn list_files() -> Vec<PathBuf> {
        VFS.list_files()
    }

    pub fn flush_to_disk(base_dir: impl AsRef<Path>) -> Result<()> {
        VFS.flush_to_disk(base_dir)
    }
}

pub struct VirtualFileSystem {
    files: DashMap<PathBuf, String>,
}

impl VirtualFileSystem {
    pub fn new() -> Self {
        Self {
            files: DashMap::new(),
        }
    }

    pub fn write(&self, path: impl AsRef<Path>, content: impl Into<String>) -> Result<()> {
        let p = path.as_ref().to_path_buf();
        self.files.insert(p, content.into());
        Ok(())
    }

    pub fn read(&self, path: impl AsRef<Path>) -> Result<String> {
        let p = path.as_ref();
        self.files
            .get(p)
            .map(|v| v.value().clone())
            .ok_or_else(|| NexyError::VfsError(format!("File not found in VFS: {:?}", p)))
    }

    pub fn exists(&self, path: impl AsRef<Path>) -> bool {
        self.files.contains_key(path.as_ref())
    }

    pub fn delete(&self, path: impl AsRef<Path>) -> Result<()> {
        let p = path.as_ref();
        self.files
            .remove(p)
            .ok_or_else(|| NexyError::VfsError(format!("File not found in VFS: {:?}", p)))?;
        Ok(())
    }

    pub fn clear(&self) {
        self.files.clear();
    }

    pub fn list_files(&self) -> Vec<PathBuf> {
        self.files.iter().map(|e| e.key().clone()).collect()
    }

    pub fn flush_to_disk(&self, base_dir: impl AsRef<Path>) -> Result<()> {
        let base = base_dir.as_ref();
        for entry in self.files.iter() {
            let full_path = base.join(entry.key());
            if let Some(parent) = full_path.parent() {
                std::fs::create_dir_all(parent)?;
            }
            std::fs::write(&full_path, entry.value().as_bytes())?;
        }
        Ok(())
    }
}
