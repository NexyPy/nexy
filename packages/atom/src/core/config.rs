use std::collections::HashMap;
use std::path::{Path, PathBuf};
use once_cell::sync::OnceCell;
use crate::core::errors::{NexyError, Result};
use crate::core::models::{FrameworkConfig, NexyConfigModel};

static INSTANCE: OnceCell<NexyConfig> = OnceCell::new();

#[derive(Debug, Clone)]
pub struct NexyConfig {
    pub model: NexyConfigModel,
    pub aliases: HashMap<String, String>,
    pub markdown_extensions: Vec<String>,
    pub frontend_extensions: HashMap<String, String>,
    pub ff_registry: HashMap<String, FrameworkConfig>,
    pub watch_extensions_glob: Vec<String>,
    pub watch_exclude_patterns: Vec<String>,
    pub namespace: String,
    pub router_path: PathBuf,
    pub project_root: PathBuf,
    pub load_error: Option<String>,
}

impl NexyConfig {
    pub fn global() -> &'static NexyConfig {
        INSTANCE.get().expect("NexyConfig not initialized")
    }

    pub fn global_try() -> Option<&'static NexyConfig> {
        INSTANCE.get()
    }

    pub fn load(path: Option<&Path>) -> Result<&'static NexyConfig> {
        let config = NexyConfig::try_load(path)?;
        INSTANCE
            .set(config)
            .map_err(|_| NexyError::ConfigError("Config already initialized".into()))?;
        Ok(INSTANCE.get().unwrap())
    }

    pub fn try_load(path: Option<&Path>) -> Result<Self> {
        let model = NexyConfigModel::default();
        let project_root = path
            .map(|p| {
                if p.is_file() {
                    p.parent().unwrap_or(p).to_path_buf()
                } else {
                    p.to_path_buf()
                }
            })
            .unwrap_or_else(|| std::env::current_dir().unwrap_or_default());

        let aliases = model.aliases.clone();
        let markdown_extensions = model.markdown_extensions.clone();
        let mut frontend_extensions = model.frontend_extensions.clone();
        let mut ff_registry = HashMap::new();

        for ff in &model.use_ff {
            let name = ff.name.to_lowercase();
            ff_registry.insert(name.clone(), ff.clone());
            for ext in &ff.extensions {
                let e = if ext.starts_with('.') {
                    ext.clone()
                } else {
                    format!(".{}", ext)
                };
                frontend_extensions.insert(e.to_lowercase(), name.clone());
            }
        }

        let watch_extensions_glob: Vec<String> = model
            .route_file_extensions
            .iter()
            .map(|e| format!("*{}", e))
            .collect();

        let model_clone = model.clone();

        Ok(Self {
            model: model_clone.clone(),
            aliases,
            markdown_extensions,
            frontend_extensions,
            ff_registry,
            watch_extensions_glob,
            watch_exclude_patterns: model_clone.watch_exclude.clone(),
            namespace: model_clone.namespace.clone(),
            router_path: project_root.join(&model_clone.router_path),
            project_root,
            load_error: None,
        })
    }

    pub fn is_nexy_file(path: &Path) -> bool {
        path.extension()
            .and_then(|e| e.to_str())
            .map(|e| e == "nexy")
            .unwrap_or(false)
    }

    pub fn is_mdx_file(path: &Path) -> bool {
        path.extension()
            .and_then(|e| e.to_str())
            .map(|e| e == "mdx")
            .unwrap_or(false)
    }

    pub fn is_route_file(&self, path: &Path) -> bool {
        let name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
        if Self::is_exception(name) {
            return false;
        }
        let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
        self.model.route_file_extensions.contains(&format!(".{}", ext))
    }

    fn is_exception(name: &str) -> bool {
        matches!(
            name,
            "__init__.py" | "layout.nexy" | "dependencies.py"
        ) || name.starts_with('_')
    }
}
