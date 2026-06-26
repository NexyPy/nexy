pub struct ScanResult {
    pub logic_block: String,
    pub template_block: String,
}

pub struct Scanner;

impl Scanner {
    pub fn scan(source: &str) -> Result<ScanResult, String> {
        let source = source.trim();

        if !source.starts_with("---") {
            // No frontmatter at all — entire file is the template
            return Ok(ScanResult {
                logic_block: String::new(),
                template_block: source.to_string(),
            });
        }

        let rest = &source[3..]; // skip opening ---
        let end = rest.find("\n---")
            .ok_or_else::<String, _>(|| "Missing closing frontmatter delimiter '---'".into())?;

        let logic_block = rest[..end].trim().to_string();
        let template_block = rest[end + 4..].trim().to_string();

        Ok(ScanResult {
            logic_block,
            template_block,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_scan_valid() {
        let source = "---\nprop[name]: str\n---\n<div>{{ name }}</div>";
        let result = Scanner::scan(source).unwrap();
        assert_eq!(result.logic_block, "prop[name]: str");
        assert_eq!(result.template_block, "<div>{{ name }}</div>");
    }

    #[test]
    fn test_scan_no_frontmatter() {
        let source = "<div>no frontmatter</div>";
        let result = Scanner::scan(source).unwrap();
        assert_eq!(result.logic_block, "");
        assert_eq!(result.template_block, "<div>no frontmatter</div>");
    }
}
