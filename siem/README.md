# Wazuh: il SIEM del laboratorio

## Obiettivo
Raccogliere in un unico posto i log delle macchine, conservarli al sicuro e analizzarli con regole di rilevamento.

## Installazione
Prima di installare ho letto i requisiti nella documentazione ufficiale di Wazuh (versione 4.14):

| Requisito | Scelta |
|---|---|
| 4 vCPU, 8 GB di RAM, 50 GB di disco | VM in UTM con queste risorse |
| Ubuntu supportato fino alla **24.04** | Ho scelto la 24.04 invece della più recente, che non era nell'elenco |
| x86_64 o ARM64 | ARM64, virtualizzato sul Mac con chip Apple |

Due correzioni **prima** di installare:
- l'installer di Ubuntu aveva assegnato al sistema solo **23 GB** su 50 → allargato con `lvextend` e `resize2fs`;
- avevo chiamato il mio utente con lo **stesso nome** dell'account di servizio che Wazuh crea per sé. Ho creato un amministratore con un altro nome ed eliminato quello vecchio: i servizi devono girare con un account proprio (**privilegio minimo**).

Installazione "tutto in uno" con lo script ufficiale, poi **agente** sul domain controller, installato con il comando generato dalla dashboard. Prima di eseguirlo l'ho letto pezzo per pezzo: download dal sito ufficiale, installazione silenziosa, indirizzo del server, nome dell'agente.

## La scoperta: una zona cieca creata da me
**Il test.** Sul domain controller ho simulato un accesso fallito di un utente di prova (`runas` con una password sbagliata), poi ho cercato l'utente nel SIEM.

**Cosa mi aspettavo:** due eventi, il **4771** (Kerberos rifiuta la password) e il **4625** (accesso fallito).

**Cosa è arrivato:** solo il 4771.

**L'indagine.** Con `auditpol /get /category:*` ho scoperto che sul domain controller erano attive solo **2 sottocategorie di audit su circa 57**: non venivano registrati accessi riusciti o falliti, creazione di utenti, modifiche ai gruppi, né le modifiche alla policy di audit stessa.

**La causa.** Settimane prima, per attivare i fallimenti di Kerberos, avevo configurato l'**Advanced Audit Policy** nella Group Policy dei domain controller. Con questa impostazione le sottocategorie **non configurate** nella GPO restano senza audit. Correggendo una zona cieca ne avevo creata una molto più grande.

**La correzione.** Ho configurato nella stessa GPO le sottocategorie che servono a un domain controller e le ho **verificate riga per riga** dopo `gpupdate /force`:

| Categoria | Sottocategorie | Eventi principali |
|---|---|---|
| Account Logon | Kerberos Authentication Service, Kerberos Service Ticket Operations, Credential Validation | 4768, 4769, 4771, 4776 |
| Logon/Logoff | Logon, Logoff, Account Lockout, Special Logon | 4624, 4625, 4634, 4740, 4672 |
| Account Management | User Account, Security Group, Computer Account Management | 4720, 4726, 4728, 4732 |
| Policy Change | Audit Policy Change, Authentication Policy Change | 4719 |
| Detailed Tracking | Process Creation | 4688 |
| DS Access | Directory Service Changes | 5136 |
| Privilege Use, System | Sensitive Privilege Use, Security State Change, Security System Extension, System Integrity | |

**La verifica.** Ripetendo il test sono arrivati **entrambi** gli eventi, con numeri di record consecutivi: lo stesso tentativo visto da due componenti diversi di Windows.

## Cosa ho imparato
- **Quello che non viene registrato non si può rilevare.** Prima di cercare un attacco, controllo che i log esistano.
- **Ogni modifica alla sicurezza va verificata dopo**, su tutto e non solo sulla parte che si voleva cambiare.
- Un SIEM serve anche ad accorgersi di **ciò che manca**.

<!-- Screenshot da aggiungere (ripuliti):
     - dashboard di Wazuh con l'agente del domain controller attivo
     - ricerca dell'utente di prova con gli eventi 4771 e 4625
     - output di auditpol prima e dopo la correzione
     NON pubblicare password, file wazuh-install-files.tar o certificati -->
