# Scansione e brute force SSH

## Scenario
Dalla macchina attaccante ho scansionato un server Ubuntu del laboratorio, poi ho provato ad accedere via SSH con utenti inesistenti e password sbagliate, e infine con le credenziali corrette.

## Cosa ho trovato
**Nel traffico (tcpdump / Wireshark):**
- migliaia di pacchetti **SYN** dallo stesso IP verso porte diverse in pochi secondi, a cui il server risponde con **RST** (porta chiusa) o **SYN-ACK** (porta aperta): la firma di una scansione;
- nella scansione rapida, l'attaccante risponde al SYN-ACK con un RST invece di completare l'handshake (*SYN scan "a metà"*);
- durante la scansione completa delle 65.535 porte, tcpdump ha perso migliaia di pacchetti (`dropped by kernel`): anche gli strumenti di monitoraggio possono perdere dati.

**Nei log del server (`auth.log`):**
- `Failed password for invalid user …` → utenti inesistenti: uno strumento che tira a indovinare;
- `Failed password for <utente>` → un utente esistente con password sbagliata;
- `Accepted password for <utente> from <IP>` → l'accesso riuscito.

```bash
sudo grep -a "Failed password" /var/log/auth.log | grep -oE "from [0-9.]+" | sort | uniq -c | sort -rn
```
(`-a` serve quando grep tratta il log come file binario, ad esempio dopo uno spegnimento brusco.)

## Mappatura MITRE ATT&CK
T1046 Network Service Discovery → T1110.001 Password Guessing → T1078 Valid Accounts

## Il ticket
| Campo | Contenuto |
|---|---|
| Titolo | Accesso SSH riuscito dopo scansione e brute force |
| Gravità | Critica: accesso ottenuto da un IP **interno**, quindi probabilmente un'altra macchina è già compromessa |
| Azioni | **E**scalation al livello 2 · **C**ontenimento: isolare le macchine, bloccare l'IP, chiudere le sessioni · **A**ccount: cambiare la password, SSH solo con chiave · **I**ndagine: cosa è stato fatto dopo l'accesso (sudo, nuovi utenti, cron, chiavi SSH) e chi usa la macchina sorgente |

## Cosa ho imparato
Lo schema **"tanti fallimenti, poi un successo"** è il più importante da riconoscere, e lo ritrovo ovunque: `Failed` → `Accepted` su Linux, 4625 → 4624 su Windows, molti 404 → un 200 sul web.
