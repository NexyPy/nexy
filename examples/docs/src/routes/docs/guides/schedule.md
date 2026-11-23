# Schedule backups

A backup you have to remember is a backup you will miss. Run Cairn every hour instead.

## Linux, with systemd

Create `~/.config/systemd/user/cairn.service`:

```ini
[Service]
Type=oneshot
Environment=CAIRN_PASSPHRASE_FILE=%h/.config/cairn/passphrase
ExecStart=%h/.local/bin/cairn backup %h/Documents
```

And `~/.config/systemd/user/cairn.timer`:

```ini
[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Then turn it on:

```bash
systemctl --user enable --now cairn.timer
```

## macOS

```bash
cairn schedule --every 1h ~/Documents
```

`cairn schedule` writes a launchd job for you and prints where it put it.

## Check that it runs

```bash
cairn snapshots --last 3
```
