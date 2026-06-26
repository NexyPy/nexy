use crate::core::errors::Result;
use crate::core::models::Component;

pub struct LogicGenerator;

impl LogicGenerator {
    pub fn generate(component: &Component) -> Result<String> {
        let mut code = String::new();

        for import in &component.imports {
            code.push_str(&format!(
                "from {} import {}\n",
                import.source,
                import.names.join(", ")
            ));
        }

        let _props_sig: Vec<String> = component
            .props
            .iter()
            .map(|p| {
                if let Some(ref default) = p.default_value {
                    format!("{}: {} = {}", p.name, p.type_name.as_deref().unwrap_or("Any"), default)
                } else {
                    format!("{}: {}", p.name, p.type_name.as_deref().unwrap_or("Any"))
                }
            })
            .collect();

        code.push_str(&format!(
            "def {}():\n    pass\n",
            component.name
        ));

        Ok(code)
    }
}
