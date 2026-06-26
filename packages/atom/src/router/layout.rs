use std::path::{Path, PathBuf};

pub struct RouteLayout;

impl RouteLayout {
    /// Walk up from `source` to find the nearest layout.nexy
    pub fn find_layout(source: &Path, routes_dir: &Path) -> Option<PathBuf> {
        let mut current = source.parent()?;

        loop {
            let layout = current.join("layout.nexy");
            if layout.exists() {
                return Some(layout);
            }

            if current == routes_dir {
                break;
            }

            current = current.parent()?;
        }

        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_find_layout() {
        let dir = std::env::temp_dir().join("nexy_layout_test");
        let _ = fs::create_dir_all(dir.join("blog"));
        let layout = dir.join("layout.nexy");
        fs::write(&layout, "").unwrap();

        let source = dir.join("blog").join("post.nexy");
        let result = RouteLayout::find_layout(&source, &dir);
        assert_eq!(result, Some(layout));

        let _ = fs::remove_dir_all(&dir);
    }
}
