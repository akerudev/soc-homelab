# Detection: rilevare un brute force in un log SSH

`conta_tentativi.py` è il mio primo programma Python per l'analisi dei log. Legge un log di autenticazione SSH, conta i tentativi falliti per indirizzo IP e assegna un livello di gravità.

## Come si usa
```bash
python3 conta_tentativi.py
```
Il log di esempio è in `dati/esempio-auth.log`: è **inventato**, con lo stesso formato del log di un server Ubuntu, e usa indirizzi IP riservati alla documentazione.

## Risultato
```
203.0.113.45      28 tentativi  (18 su utenti inesistenti ) 🚨 CRITICO: brute force RIUSCITO
192.0.2.77         6 tentativi  (6 su utenti inesistenti ) ⚠️  ALERT: possibile brute force
198.51.100.23      4 tentativi  (4 su utenti inesistenti ) ⚠️  ALERT: possibile attacco con utenti non esistenti
10.0.2.10          1 tentativi  (0 su utenti inesistenti )
```

## Le regole di rilevamento
| Livello | Condizione | Perché |
|---|---|---|
| 🚨 CRITICO | Almeno 5 tentativi falliti **e** almeno un accesso riuscito dallo stesso IP | Dopo il successo non è più un tentativo: l'account è compromesso |
| ⚠️ ALERT | Almeno 5 tentativi falliti | Possibile brute force |
| ⚠️ ALERT (utenti inesistenti) | Almeno 3 tentativi su utenti che non esistono | Uno scanner lento resta sotto la soglia, ma prova nomi a caso |
| nessuno | Il resto | Un collega che sbaglia la password una volta non è un attacco |

## Il limite che ho scoperto
La prima versione usava solo la soglia di 5 tentativi. Lo scanner `198.51.100.23` faceva un tentativo ogni 10–15 minuti e restava sotto la soglia: un **falso negativo**. Ho aggiunto un secondo criterio, i tentativi su utenti inesistenti, e il programma ha iniziato a segnalarlo.

> Una soglia fissa ferma gli attaccanti rumorosi, non quelli pazienti ("low and slow").

## Errori da cui ho imparato
- **Una variabile non ricalcolata nel ciclo** faceva contare tutti i tentativi sotto un solo IP, senza nessun messaggio di errore: il bug più pericoloso è quello che dà risultati sbagliati in silenzio.
- **L'ordine conta:** in Python una variabile va creata prima di essere usata (`NameError`).

## Possibili sviluppi
- finestre temporali ("più di N tentativi in 10 minuti");
- lettura del file da riga di comando invece che dal percorso fisso;
- confronto degli IP con servizi di reputazione.
