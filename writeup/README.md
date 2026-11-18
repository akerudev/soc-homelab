# Writeup delle indagini

Ogni indagine è stata svolta nel mio laboratorio: prima simulo l'attività, poi la cerco nei log come farebbe un analista che non sa cosa è successo.

| # | Indagine | Fonti dei log | MITRE ATT&CK |
|---|---|---|---|
| 1 | [Scansione e brute force SSH](01-scansione-e-brute-force-ssh.md) | `auth.log`, tcpdump | T1046 → T1110.001 → T1078 |
| 2 | [Persistenza su Linux](02-persistenza-linux.md) | journal di systemd, `auth.log` | T1078 → T1003.008 → T1136.001 → T1098 → T1053.003 → T1070 |
| 3 | [Accesso fallito in un dominio Windows](03-accesso-fallito-dominio.md) | Security log di DC e client, Wazuh | T1110 |
