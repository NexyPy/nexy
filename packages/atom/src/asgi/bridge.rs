use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::path::Path;

use crate::builder::Builder;
use crate::builder::Discovery;
use crate::compiler::Compiler;
use crate::core::config::NexyConfig;
use crate::core::vfs::Vfs;
use crate::router::fbrouter::FbRouter;
use crate::router::layout::RouteLayout;

/// Nexy core engine exposed to Python via PyO3.
///
/// Usage from Python:
/// ```python
/// from nexy_atom import NexyCore
///
/// core = NexyCore()
/// core.load_config(".")
/// core.build("src")
/// routes = core.discover_routes("src/routes")
/// ```
#[pyclass(name = "NexyCore")]
pub struct PyNexyCore;

#[pymethods]
impl PyNexyCore {
    #[new]
    pub fn new() -> Self {
        Self
    }

    /// Load nexyconfig from project root directory.
    #[staticmethod]
    pub fn load_config(path: Option<&str>) -> PyResult<()> {
        let config_path = path.map(Path::new);
        NexyConfig::load(config_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    /// Compile a single .nexy or .mdx file.
    /// Returns the output path on success.
    pub fn compile(input: &str, output: Option<&str>) -> PyResult<String> {
        let mut compiler = Compiler::new();
        compiler
            .compile(input, output.map(String::from))
            .map(|_| "ok".to_string())
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    /// Build all .nexy / .mdx files under root_dir.
    /// Returns a dict with total/success/failed.
    pub fn build(root_dir: &str) -> PyResult<PyObject> {
        let builder = Builder::new();
        let result = builder
            .build(Path::new(root_dir))
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("total", result.total).unwrap();
            dict.set_item("success", result.success).unwrap();
            let failures: Vec<String> = result
                .failed
                .iter()
                .map(|(f, e)| format!("{}: {}", f, e))
                .collect();
            dict.set_item("failed", failures).unwrap();
            Ok(dict.into())
        })
    }

    /// Discover all .nexy / .mdx files under root_dir.
    /// Returns a list of file paths.
    #[staticmethod]
    pub fn discover_files(root_dir: &str) -> PyResult<Vec<String>> {
        let files = Discovery::scan(Path::new(root_dir))
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
        Ok(files.into_iter().map(|f| f.to_string_lossy().to_string()).collect())
    }

    /// Discover file-based routes from routes_dir.
    /// Returns a list of dicts with path, file, is_dynamic, params.
    #[staticmethod]
    pub fn discover_routes(routes_dir: &str) -> PyResult<Vec<PyObject>> {
        let fb = FbRouter::new(Path::new(routes_dir).to_path_buf());
        let routes = fb
            .discover()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        Python::with_gil(|py| {
            let out: Vec<PyObject> = routes
                .iter()
                .map(|r| {
                    let d = PyDict::new(py);
                    d.set_item("path", &r.path).unwrap();
                    d.set_item("file", &r.file).unwrap();
                    d.set_item("is_dynamic", r.is_dynamic).unwrap();
                    d.set_item("params", r.params.clone()).unwrap();
                    d.into()
                })
                .collect();
            Ok(out)
        })
    }

    /// Find the nearest layout.nexy for a source file.
    #[staticmethod]
    fn find_layout(source: &str, routes_dir: &str) -> PyResult<Option<String>> {
        let result = RouteLayout::find_layout(
            Path::new(source),
            Path::new(routes_dir),
        );
        Ok(result.map(|p| p.to_string_lossy().to_string()))
    }

    // --- Virtual Filesystem (VFS) operations ---

    #[staticmethod]
    pub fn vfs_write(path: &str, content: &str) -> PyResult<()> {
        Vfs::write(path, content)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    #[staticmethod]
    pub fn vfs_read(path: &str) -> PyResult<String> {
        Vfs::read(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    #[staticmethod]
    pub fn vfs_exists(path: &str) -> bool {
        Vfs::exists(path)
    }

    #[staticmethod]
    pub fn vfs_delete(path: &str) -> PyResult<()> {
        Vfs::delete(path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    #[staticmethod]
    pub fn vfs_clear() {
        Vfs::clear();
    }

    #[staticmethod]
    pub fn vfs_flush(base_dir: &str) -> PyResult<()> {
        Vfs::flush_to_disk(base_dir)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
    }

    #[staticmethod]
    pub fn version() -> &'static str {
        "2.0.9"
    }
}

#[pymodule]
fn nexy_atom(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyNexyCore>()?;
    m.add("__version__", "2.0.9")?;
    Ok(())
}
