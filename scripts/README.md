# Shell scripts

Run these from the **repository root** (or use `make` targets, which invoke them for you).

| Script | Purpose |
|--------|---------|
| `startup-dev.sh` | Dev: MongoDB + Temporal in Docker; then seed DB |
| `shutdown-dev.sh` | Stop dev infrastructure |
| `startup-prod.sh` | Prod: full stack in Docker |
| `shutdown-prod.sh` | Stop prod stack |
| `startup-legacy.sh` | Legacy: `docker-compose.legacy.yml` full stack |
| `shutdown-legacy.sh` | Stop legacy stack |
| `dcompose` | Wrapper: same as `docker compose` / `docker-compose` (see `lib/compose.sh`) |
| `lib/compose.sh` | Detects working Compose CLI (V2 plugin or standalone v1) |

```bash
chmod +x scripts/*.sh scripts/dcompose
./scripts/startup-dev.sh
```

Compose detection: **`docker compose`** first; if the CLI plugin is missing or broken, **`docker-compose`** is used when available.
