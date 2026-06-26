use std::collections::HashMap;
use serde::{Deserialize, Serialize};

/// Represents a parsed .nexy component
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Component {
    pub name: String,
    pub props: Vec<Prop>,
    pub imports: Vec<Import>,
    pub python_code: String,
    pub template: String,
    pub source_path: String,
    pub framework: Option<String>,
}

/// A prop declaration from frontmatter: `prop[Type]`
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Prop {
    pub name: String,
    pub type_name: Option<String>,
    pub default_value: Option<String>,
}

/// An import declaration from frontmatter: `from "file.nexy" import X`
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Import {
    pub source: String,
    pub names: Vec<String>,
    pub alias: Option<String>,
    pub framework: Option<String>,
}

/// AST node for template parsing
#[derive(Debug, Clone)]
pub enum Node {
    Text(String),
    Element(ElementNode),
    Component(ComponentNode),
    JinjaBlock(String),
    JinjaExpr(String),
}

#[derive(Debug, Clone)]
pub struct ElementNode {
    pub tag: String,
    pub attributes: HashMap<String, String>,
    pub children: Vec<Node>,
    pub self_closing: bool,
}

#[derive(Debug, Clone)]
pub struct ComponentNode {
    pub name: String,
    pub props: HashMap<String, String>,
    pub children: Vec<Node>,
    pub self_closing: bool,
}

/// A route registered by the router
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Route {
    pub path: String,
    pub file: String,
    pub component: Option<String>,
    pub methods: Vec<String>,
    pub is_dynamic: bool,
    pub params: Vec<String>,
}

/// Result of a build operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BuildResult {
    pub success: Vec<String>,
    pub failed: Vec<(String, String)>,
    pub total: usize,
}

/// Nexy configuration model (mirrors NexyConfigModel from Python)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NexyConfigModel {
    pub namespace: String,
    pub router_path: String,
    pub project_root: String,
    pub target_extensions: Vec<String>,
    pub route_file_extensions: Vec<String>,
    pub route_file_exceptions: Vec<String>,
    pub route_file_default: Vec<String>,
    pub frontend_extensions: HashMap<String, String>,
    pub watch_extensions: Vec<String>,
    pub watch_exclude: Vec<String>,
    pub aliases: HashMap<String, String>,
    pub markdown_extensions: Vec<String>,
    pub use_cors: Option<serde_json::Value>,
    pub use_gzip: Option<serde_json::Value>,
    pub use_trusted_host: Option<serde_json::Value>,
    pub use_session: Option<serde_json::Value>,
    pub use_auth: Option<serde_json::Value>,
    pub use_https_redirect: bool,
    pub use_docs: bool,
    pub use_docs_url: Option<String>,
    pub use_redocs_url: Option<String>,
    pub use_router: Option<String>,
    pub use_ff: Vec<FrameworkConfig>,
    pub title: Option<String>,
    pub host: Option<String>,
    pub port: Option<u16>,
}

impl Default for NexyConfigModel {
    fn default() -> Self {
        let mut frontend_extensions = HashMap::new();
        frontend_extensions.insert(".tsx".into(), "react".into());
        frontend_extensions.insert(".jsx".into(), "react".into());
        frontend_extensions.insert(".vue".into(), "vue".into());
        frontend_extensions.insert(".svelte".into(), "svelte".into());

        Self {
            namespace: "__nexy__/".into(),
            router_path: "src/routes".into(),
            project_root: ".".into(),
            target_extensions: vec![".nexy".into(), ".mdx".into()],
            route_file_extensions: vec![".nexy".into(), ".mdx".into(), ".py".into()],
            route_file_exceptions: vec![
                "__init__.py".into(),
                "layout.nexy".into(),
                "dependencies.py".into(),
            ],
            route_file_default: vec![
                "index.py".into(),
                "index.nexy".into(),
                "index.mdx".into(),
            ],
            frontend_extensions,
            watch_extensions: vec!["*.py".into(), "*.mdx".into(), "*.nexy".into()],
            watch_exclude: vec![
                "*/.git/*".into(),
                "*/.venv/*".into(),
                "*/__nexy__/*".into(),
                "*/__pycache__/*".into(),
                "*/node_modules/*".into(),
            ],
            aliases: HashMap::new(),
            markdown_extensions: vec![
                "extra".into(),
                "tables".into(),
                "fenced_code".into(),
                "codehilite".into(),
                "toc".into(),
                "admonition".into(),
                "attr_list".into(),
                "pymdownx.highlight".into(),
                "pymdownx.superfences".into(),
            ],
            use_cors: None,
            use_gzip: None,
            use_trusted_host: None,
            use_session: None,
            use_auth: None,
            use_https_redirect: false,
            use_docs: true,
            use_docs_url: None,
            use_redocs_url: None,
            use_router: None,
            use_ff: Vec::new(),
            title: None,
            host: None,
            port: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FrameworkConfig {
    pub name: String,
    pub extensions: Vec<String>,
}

/// Parser model returned after compiling a .nexy file
#[derive(Debug, Clone)]
pub struct ParserModel {
    pub component: Component,
    pub dependencies: Vec<String>,
    pub css_imports: Vec<String>,
    pub layout: Option<String>,
}
