use std::path::Path;
use crate::core::errors::{NexyError, Result};
use crate::core::models::Import;

pub struct ImportValidator;

impl ImportValidator {
    pub fn validate(imports: &[Import], _current_file: &Path) -> Result<()> {
        for import in imports {
            let target_path = Path::new(&import.source);
            if target_path.is_absolute() && !target_path.exists() {
                return Err(NexyError::parse(format!(
                    "Imported file not found: {}",
                    import.source
                )));
            }
        }
        Ok(())
    }
}
