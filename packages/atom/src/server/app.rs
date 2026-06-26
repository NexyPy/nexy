use std::sync::Arc;
use axum::{
    Router,
    routing::get,
    response::Html,
};
use tower_http::cors::CorsLayer;
use tower_http::compression::CompressionLayer;
use crate::core::config::NexyConfig;
use crate::core::errors::Result;
use crate::router::Router as NexyRouter;
use crate::router::fbrouter::FbRouter;
use crate::server::hmr::HmrState;

pub struct AppServer {
    router: Option<NexyRouter>,
    config: Arc<NexyConfig>,
    hmr: Arc<HmrState>,
}

impl AppServer {
    pub fn new() -> Self {
        let config = Arc::new(NexyConfig::global().clone());
        Self {
            router: None,
            config,
            hmr: Arc::new(HmrState::new()),
        }
    }

    pub fn build(&mut self) -> Result<Router> {
        let mut app = Router::new();

        self.setup_static_files(&mut app);
        self.setup_middlewares(&mut app);
        self.resolve_router(&mut app)?;
        self.setup_hmr(&mut app);

        Ok(app)
    }

    fn setup_static_files(&self, _app: &mut Router) {
    }

    fn setup_middlewares(&self, app: &mut Router) {
        let mut router = Router::new();
        std::mem::swap(app, &mut router);
        if self.config.model.use_cors.is_some() {
            router = router.layer(CorsLayer::permissive());
        }
        if self.config.model.use_gzip.is_some() {
            router = router.layer(CompressionLayer::new());
        }
        *app = router;
    }

    fn resolve_router(&mut self, app: &mut Router) -> Result<()> {
        let routes_dir = &self.config.router_path;
        if routes_dir.exists() {
            let fb_router = FbRouter::new(routes_dir.clone());
            let routes = fb_router.discover()?;

            let mut router = Router::new();
            std::mem::swap(app, &mut router);

            for route in &routes {
                let path = &route.path;
                let handler_path = path.clone();
                let handler = move || async move {
                    Html(format!("<h1>Nexy: {}</h1>", handler_path))
                };
                router = router.route(path, get(handler));
            }
            *app = router;
        }
        Ok(())
    }

    fn setup_hmr(&self, _app: &mut Router) {
        // HMR WebSocket requires axum's ws feature
    }
}

impl Default for AppServer {
    fn default() -> Self {
        Self::new()
    }
}
