# Accesso fallito in un dominio Windows

## Scenario
In un dominio Active Directory costruito da zero, un utente di prova sbaglia la password accedendo a un PC del dominio. Obiettivo: trovare il tentativo nei log **di entrambe le macchine** e collegarli.

## Prima sorpresa: il domain controller non registrava i fallimenti
Il 4771 non compariva. `auditpol` mostrava *Kerberos Authentication Service: Success*: le password sbagliate non venivano registrate. Ho attivato i fallimenti tramite Group Policy, scoprendo che il vecchio metodo (*Audit Policy*) viene ignorato e che serve l'**Advanced Audit Policy**.

(Settimane dopo, il SIEM mi ha mostrato che quella stessa correzione aveva spento tutte le altre sottocategorie: vedi [siem/](../siem/README.md).)

## La correlazione
| Ora | Macchina | Evento | Dettagli |
|---|---|---|---|
| 15:08:38 | DC | **4719** | La mia modifica alla policy di audit è stata registrata |
| 15:10:33 | **DC** | **4771** | Kerberos rifiuta la password (failure code `0x18`), richiesta dall'IP del client |
| 15:10:33 | **Client** | **4625** | Accesso fallito, Logon Type 2 (davanti al PC) |
| 15:10:50 | DC | **4768** | Biglietto Kerberos rilasciato: password giusta 17 secondi dopo |

Lo stesso tentativo, nello stesso secondo, visto da due macchine. Il client dice *dove* è avvenuto, il domain controller *chi* ha verificato la password.

## Cosa cerca un analista
- Molti **4771** per lo stesso utente → qualcuno prova la sua password.
- Molti **4771** su utenti diversi, poche prove ciascuno → possibile *password spraying*. Sui singoli PC sembra innocuo: solo il domain controller ha il quadro completo.
- Un **4719** è sempre da guardare: lo stesso evento può indicare chi accende l'audit, come in questo caso, o chi lo spegne per nascondersi (T1562.002).

## Mappatura MITRE ATT&CK
T1110 Brute Force (Credential Access) · T1562.002 Impair Defenses: Disable Windows Event Logging
