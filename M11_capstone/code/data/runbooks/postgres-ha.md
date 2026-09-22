# postgres-ha runbook

1. `cnpg status postgres-ha` — three instances, one primary.
2. Check replication lag before anything else.
3. Failover only after confirming `synchronous_standby_names`.
4. Never restart two instances together.
