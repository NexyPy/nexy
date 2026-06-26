use std::collections::HashMap;
use sha2::{Sha256, Digest};

pub struct ActionEngine {
    actions: HashMap<String, ActionEntry>,
}

struct ActionEntry {
    module: String,
    function: String,
    _hash: String,
}

impl ActionEngine {
    pub fn new() -> Self {
        Self {
            actions: HashMap::new(),
        }
    }

    pub fn register(&mut self, module: &str, function: &str) -> String {
        let key = format!("{}.{}", module, function);
        let hash = hex_encode(&Sha256::digest(key.as_bytes())[..8]);
        self.actions.insert(
            hash.clone(),
            ActionEntry {
                module: module.to_string(),
                function: function.to_string(),
                _hash: hash.clone(),
            },
        );
        hash
    }

    pub fn resolve(&self, hash: &str) -> Option<(&str, &str)> {
        self.actions
            .get(hash)
            .map(|e| (e.module.as_str(), e.function.as_str()))
    }

}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

impl Default for ActionEngine {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register_and_resolve() {
        let mut engine = ActionEngine::new();
        let hash = engine.register("my_module", "my_function");
        let resolved = engine.resolve(&hash);
        assert_eq!(resolved, Some(("my_module", "my_function")));
    }
}
