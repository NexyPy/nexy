use std::path::PathBuf;
use crate::core::config::NexyConfig;
use crate::core::errors::Result;
use crate::core::models::Route;

pub struct FbRouter {
    routes_dir: PathBuf,
}

impl FbRouter {
    pub fn new(routes_dir: PathBuf) -> Self {
        Self { routes_dir }
    }

    pub fn discover(&self) -> Result<Vec<Route>> {
        let config = NexyConfig::global();
        let mut routes = Vec::new();

        if !self.routes_dir.exists() {
            return Ok(routes);
        }

        let walker = walkdir::WalkDir::new(&self.routes_dir)
            .into_iter()
            .filter_entry(|e| {
                let name = e.file_name().to_string_lossy();
                !name.starts_with('.')
                    && !name.starts_with('_')
                    && name != "node_modules"
                    && name != "__pycache__"
            });

        for entry in walker.filter_map(|e| e.ok()) {
            if !entry.file_type().is_file() {
                continue;
            }

            let path = entry.path();
            if !config.is_route_file(path) {
                continue;
            }

            let route_path = path
                .strip_prefix(&self.routes_dir)
                .unwrap_or(path)
                .to_string_lossy()
                .to_string();

            let route_path = normalize_route_path(&route_path);
            let is_dynamic = route_path.contains('{');
            let params = extract_params(&route_path);

            routes.push(Route {
                path: route_path,
                file: path.to_string_lossy().to_string(),
                component: None,
                methods: vec!["GET".into()],
                is_dynamic,
                params,
            });
        }

        Ok(routes)
    }
}

fn normalize_route_path(path: &str) -> String {
    let path = path
        .replace('\\', "/")
        .replace("[", "{")
        .replace("]", "}");

    let stripped = path
        .strip_suffix("/index.nexy")
        .or_else(|| path.strip_suffix("/index.py"))
        .or_else(|| path.strip_suffix("/index.mdx"))
        .or_else(|| path.strip_suffix(".nexy"))
        .or_else(|| path.strip_suffix(".py"))
        .or_else(|| path.strip_suffix(".mdx"))
        .map(|s| s.to_string())
        .unwrap_or(path);

    if stripped.is_empty() || stripped == "index" || stripped == "/index" {
        "/".to_string()
    } else if !stripped.starts_with('/') {
        format!("/{}", stripped)
    } else {
        stripped
    }
}

fn extract_params(path: &str) -> Vec<String> {
    let mut params = Vec::new();
    for segment in path.split('/') {
        if segment.starts_with('{') && segment.ends_with('}') {
            params.push(segment[1..segment.len() - 1].to_string());
        }
    }
    params
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_normalize_route_path() {
        assert_eq!(normalize_route_path("index.nexy"), "/");
        assert_eq!(normalize_route_path("about.nexy"), "/about");
        assert_eq!(normalize_route_path("blog/[slug].nexy"), "/blog/{slug}");
    }
}
