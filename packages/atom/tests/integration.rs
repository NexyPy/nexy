#[cfg(test)]
mod tests {
use nexy_atom::compiler::Compiler;

    /// Find the root docs/ directory from the repo root
    fn find_docs_dir() -> std::path::PathBuf {
        let root = std::env::current_dir()
            .unwrap()
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .to_path_buf();
        let docs = root.join("docs");
        assert!(
            docs.join("src/routes").exists(),
            "Root docs/ not found at {:?}",
            docs
        );
        docs
    }

    #[test]
    fn test_docs_compile_all_nexy_files() {
        let docs_dir = find_docs_dir();
        let src_dir = docs_dir.join("src");

        let nexy_files: Vec<_> = walkdir::WalkDir::new(&src_dir)
            .into_iter()
            .filter_entry(|e| {
                let name = e.file_name().to_string_lossy();
                !name.starts_with('.')
                    && name != "__pycache__"
                    && name != "node_modules"
            })
            .filter_map(|e| e.ok())
            .filter(|e| {
                e.file_type().is_file()
                    && e.path().extension().map(|x| x == "nexy").unwrap_or(false)
            })
            .map(|e| e.path().to_path_buf())
            .collect();

        assert!(!nexy_files.is_empty(), "No .nexy files found in docs/src/");
        println!("Found {} .nexy files in docs/src/", nexy_files.len());

        let mut success = 0;
        let mut failed = 0;

        for file in &nexy_files {
            let rel = file.strip_prefix(&docs_dir).unwrap_or(file);
            let mut compiler = Compiler::new();
            match compiler.compile(file, None) {
                Ok(()) => {
                    println!("  ✓ {}", rel.display());
                    success += 1;
                }
                Err(e) => {
                    println!("  ✗ {} — {}", rel.display(), e);
                    failed += 1;
                }
            }
        }

        println!("\nResult: {success} passed, {failed} failed out of {}", nexy_files.len());
        assert!(success > 0, "At least some files must compile");
    }

    #[test]
    fn test_docs_specific_route_index() {
        let docs_dir = find_docs_dir();
        let file = docs_dir.join("src/routes/index.nexy");
        assert!(file.exists(), "index.nexy not found");
        let mut compiler = Compiler::new();
        compiler.compile(&file, None).expect("index.nexy should compile");
    }

    #[test]
    fn test_docs_specific_card() {
        let docs_dir = find_docs_dir();
        let file = docs_dir.join("src/components/card.nexy");
        assert!(file.exists());
        let mut compiler = Compiler::new();
        compiler.compile(&file, None).expect("card.nexy should compile");
    }

    #[test]
    fn test_docs_background() {
        let docs_dir = find_docs_dir();
        let file = docs_dir.join("src/components/background.nexy");
        assert!(file.exists());
        let mut compiler = Compiler::new();
        compiler.compile(&file, None).expect("background.nexy should compile");
    }
}
