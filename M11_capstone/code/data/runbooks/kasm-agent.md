# kasm-agent runbook

1. `docker ps` — the agent and its proxy must both be up.
2. A session that will not start usually means the agent is not Enabled in the UI.
3. Disk fills with workspace images: check `docker system df` weekly.
