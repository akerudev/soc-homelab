# Persistenza su Linux: ricostruire la timeline

## Scenario
Su un server Ubuntu ho simulato le azioni di un attaccante già entrato via SSH: lettura del file delle password cifrate, creazione di un account "di riserva", aggiunta al gruppo degli amministratori, un'attività pianificata, e infine la cancellazione di tutto. Poi, da analista, ho ricostruito la sequenza dai log.

## Comandi di ricerca
```bash
sudo journalctl -t useradd -t usermod -t su -t crontab -t userdel -o short-iso --since <data>
sudo journalctl -u ssh -o short-iso --since <data> | grep -a Accepted
sudo journalctl _COMM=sudo -o short-iso --since <data> | grep -a COMMAND
id <utente>
```

## Timeline (UTC)
| Ora | Evento | Tecnica |
|---|---|---|
| 14:44 | Accesso SSH riuscito da un IP interno | T1078 |
| 14:45 | `sudo cat /etc/shadow` | T1003.008 |
| 14:46 | Creato un nuovo account | T1136.001 |
| 14:51 | Account aggiunto al gruppo `sudo` | T1098 |
| 14:51–14:53 | 5 tentativi `su` falliti | — |
| 14:54 | Accesso con il nuovo account | — |
| 14:57 | Creata un'attività cron ogni 5 minuti, eseguita dalle 15:00 | T1053.003 |
| 15:34 | Attività e account cancellati | T1070 |

## Cosa ho imparato
- **Anche la cancellazione lascia tracce:** `userdel` registra ogni pezzo rimosso. Un account creato e cancellato nel giro di un'ora è sospetto di per sé.
- **I log correggono la memoria:** ero convinto che un comando fosse stato eseguito da un utente, il log diceva un altro. Un analista si fida delle prove.
- **Se una fonte non basta, se ne usa un'altra:** una riga mancava in `auth.log` ma c'era nel journal; lo stato attuale del sistema (`id <utente>`) ha confermato il resto.
- **Persistenza e privilege escalation:** "serve a restare o tornare?" → persistenza; "serve a diventare più potente adesso?" → privilege escalation.
