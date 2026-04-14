#!/usr/bin/env bash
# Unified Docker Compose invocation.
# Prefer Compose V2 (`docker compose`); if the CLI plugin is missing or broken,
# fall back to standalone `docker-compose` (e.g. pip install docker-compose).

compose_detected=""

compose_init() {
  # Prefer V2 when it actually works (some installs register a broken plugin).
  if docker compose version &>/dev/null 2>&1; then
    compose_detected="v2"
    return 0
  fi
  # Standalone binary (common when the CLI plugin path is missing).
  if command -v docker-compose &>/dev/null && docker-compose version &>/dev/null 2>&1; then
    compose_detected="v1"
    return 0
  fi
  echo "Error: No working Docker Compose command found." >&2
  echo "  - Repair Docker Desktop / Compose V2 plugin (~/.docker/cli-plugins/), or" >&2
  echo "  - Install standalone: brew install docker-compose   (or: pip install docker-compose)" >&2
  return 1
}

# Run compose with the same arguments you would pass to `docker compose` / `docker-compose`.
compose() {
  if [[ -z "$compose_detected" ]]; then
    compose_init || return 1
  fi
  if [[ "$compose_detected" == "v2" ]]; then
    docker compose "$@"
  else
    docker-compose "$@"
  fi
}
