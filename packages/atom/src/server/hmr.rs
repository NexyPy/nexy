use tokio::sync::broadcast;

#[derive(Clone)]
pub struct HmrState {
    tx: broadcast::Sender<String>,
}

impl HmrState {
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(100);
        Self { tx }
    }

    pub fn reload(&self) {
        let _ = self.tx.send("nexy:reload".to_string());
    }
}

impl Default for HmrState {
    fn default() -> Self {
        Self::new()
    }
}
