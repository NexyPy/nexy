use std::path::Path;
use crate::core::models::{Import, Prop};

pub struct LogicResult {
    pub props: Vec<Prop>,
    pub imports: Vec<Import>,
    pub python_code: String,
    pub dependencies: Vec<String>,
    pub css_imports: Vec<String>,
}

pub struct LogicParser;

impl LogicParser {
    pub fn process(logic: &str, _file_path: &Path) -> Result<LogicResult, String> {
        let mut props = Vec::new();
        let mut imports = Vec::new();
        let mut python_lines = Vec::new();

        for line in logic.lines() {
            let line = line.trim();

            if line.is_empty() {
                continue;
            }

            if line.contains("prop[") && !line.starts_with("from ") && !line.starts_with("import ") {
                if let Some(prop) = Self::parse_prop(line) {
                    props.push(prop);
                }
                continue;
            }

            if line.starts_with("from ") {
                if let Some(import) = Self::parse_import(line) {
                    imports.push(import);
                }
                continue;
            }

            if line.starts_with("import ") || line.starts_with("from") {
                python_lines.push(line);
                continue;
            }

            python_lines.push(line);
        }

        Ok(LogicResult {
            props,
            imports,
            python_code: python_lines.join("\n"),
            dependencies: Vec::new(),
            css_imports: Vec::new(),
        })
    }

    fn parse_prop(line: &str) -> Option<Prop> {
        let line = line.trim();

        // Format 1: prop[type]: name
        // Format 2: name : prop[type]
        // Format 3: name:prop[type]

        if let Some(prop_start) = line.find("prop[") {
            let before = line[..prop_start].trim();

            let rest = &line[prop_start + 5..];
            let end_bracket = rest.find(']')?;
            let type_name = rest[..end_bracket].to_string();
            let after_bracket = rest[end_bracket + 1..].trim();

            // Determine name from before or after prop[...]
            let name = if before.is_empty() || before == ":" {
                // Format: prop[type]: name
                after_bracket
                    .strip_prefix(':')
                    .unwrap_or(after_bracket)
                    .trim()
                    .to_string()
            } else {
                // Format: name : prop[type]
                before
                    .strip_suffix(':')
                    .unwrap_or(before)
                    .trim()
                    .to_string()
            };

            let (name, default) = if let Some(eq_pos) = name.find('=') {
                let n = name[..eq_pos].trim().to_string();
                let d = name[eq_pos + 1..].trim().to_string();
                (n, Some(d))
            } else {
                (name, None)
            };

            if name.is_empty() || name.starts_with("from") {
                return None;
            }

            return Some(Prop {
                name,
                type_name: Some(type_name),
                default_value: default,
            });
        }

        None
    }

    fn parse_import(line: &str) -> Option<Import> {
        let line = line.trim();
        if !line.starts_with("from ") {
            return None;
        }

        let rest = &line[5..];
        let parts: Vec<&str> = rest.splitn(2, " import ").collect();
        if parts.len() != 2 {
            return None;
        }

        let source = parts[0].trim().trim_matches('"').trim_matches('\'').to_string();
        let names_part = parts[1].trim();

        let mut names = Vec::new();
        for item in names_part.split(',') {
            let item = item.trim();
            if item.is_empty() {
                continue;
            }
            // Handle "import X as Y"
            if let Some(as_pos) = item.find(" as ") {
                let alias = item[as_pos + 4..].trim().to_string();
                names.push(alias);
            } else {
                names.push(item.to_string());
            }
        }

        Some(Import {
            source,
            names,
            alias: None,
            framework: None,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_prop_legacy() {
        let line = "prop[str]: name";
        let prop = LogicParser::parse_prop(line).unwrap();
        assert_eq!(prop.name, "name");
        assert_eq!(prop.type_name, Some("str".into()));
        assert_eq!(prop.default_value, None);
    }

    #[test]
    fn test_parse_prop_real_world() {
        let line = "className : prop[str]";
        let prop = LogicParser::parse_prop(line).unwrap();
        assert_eq!(prop.name, "className");
        assert_eq!(prop.type_name, Some("str".into()));
    }

    #[test]
    fn test_parse_prop_compact() {
        let line = "children:prop[str]";
        let prop = LogicParser::parse_prop(line).unwrap();
        assert_eq!(prop.name, "children");
        assert_eq!(prop.type_name, Some("str".into()));
    }

    #[test]
    fn test_prop_with_default() {
        let line = "prop[int]: count = 0";
        let prop = LogicParser::parse_prop(line).unwrap();
        assert_eq!(prop.name, "count");
        assert_eq!(prop.default_value, Some("0".into()));
    }

    #[test]
    fn test_parse_import_simple() {
        let line = r#"from "components/Button.nexy" import Button"#;
        let import = LogicParser::parse_import(line).unwrap();
        assert_eq!(import.source, "components/Button.nexy");
        assert_eq!(import.names, vec!["Button"]);
    }

    #[test]
    fn test_parse_import_with_alias() {
        let line = r#"from "@/components/sections/home/Hero.nexy" import Hero as HeroSection"#;
        let import = LogicParser::parse_import(line).unwrap();
        assert_eq!(import.source, "@/components/sections/home/Hero.nexy");
        assert_eq!(import.names, vec!["HeroSection"]);
    }

    #[test]
    fn test_process_docs_card() {
        let logic = "className : prop[str]";
        let file_path = Path::new("card.nexy");
        let result = LogicParser::process(logic, file_path).unwrap();
        assert_eq!(result.props.len(), 1);
        assert_eq!(result.props[0].name, "className");
        assert_eq!(result.props[0].type_name.as_deref(), Some("str"));
    }

    #[test]
    fn test_process_docs_layout() {
        let logic = r#"from "@/components/docs/sidebar.nexy" import Sidebar
from "@/components/docs/table_of_contents.nexy" import Table_of_contents
children:prop[str]"#;
        let file_path = Path::new("layout.nexy");
        let result = LogicParser::process(logic, file_path).unwrap();
        assert_eq!(result.imports.len(), 2);
        assert_eq!(result.props.len(), 1);
        assert_eq!(result.props[0].name, "children");
    }

    #[test]
    fn test_process_docs_index() {
        let logic = r#"from "@/components/sections/home/Hero.nexy" import Hero as HeroSection
from "@/components/sections/home/ContentBar.nexy" import ContentBar
from "@/components/sections/home/BaseSection.nexy" import BaseSection"#;
        let file_path = Path::new("index.nexy");
        let result = LogicParser::process(logic, file_path).unwrap();
        assert_eq!(result.imports.len(), 3);
        assert_eq!(result.imports[0].names, vec!["HeroSection"]);
    }
}
