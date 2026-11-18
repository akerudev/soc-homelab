# pfSense: il firewall del laboratorio

## Obiettivo
Far passare tutto il traffico del dominio da un firewall, per poterlo **controllare** con regole e **vedere** nei log, come in una rete aziendale.

## Cosa ho fatto
1. **Installato pfSense 2.9** in UTM con due schede di rete:
   - **WAN** sulla rete condivisa del Mac (verso Internet);
   - **LAN** sulla rete isolata del dominio.
2. **Corretto l'indirizzo della LAN.** Dopo l'installazione la LAN aveva l'indirizzo predefinito `192.168.1.1`, ma il dominio usa la rete `192.168.128.0/24`: nessuna macchina poteva raggiungerlo. L'ho portata a `192.168.128.254` dalla console.
3. **Non ho attivato il DHCP sulla LAN**, perché la rete isolata ne aveva già uno: due server DHCP sulla stessa rete assegnano indirizzi e gateway a caso.
4. **Cambiato la password predefinita** dell'interfaccia web: le credenziali predefinite sono pubbliche e sono le prime che un attaccante prova.
5. **Reso pfSense il gateway del dominio:**
   - sul domain controller: gateway `192.168.128.254`;
   - nel DNS del dominio: **forwarder** verso pfSense, così i nomi di Internet vengono risolti passando dal firewall.
   - Verifica: `nslookup microsoft.com` dal domain controller restituisce una *Non-authoritative answer*.

## Una regola e i suoi log
Ho creato sulla LAN una regola di prova che blocca il protocollo ICMP (il `ping`) verso l'esterno, con la registrazione attiva.

- Dal domain controller: `ping 8.8.8.8` → *Request timed out*.
- In **Status → System Logs → Firewall**: una riga bloccata per ogni ping, circa ogni 5 secondi, con orario, interfaccia, regola applicata, sorgente e destinazione.

Nei log c'era anche del **rumore di fondo**: richieste DHCP (`0.0.0.0:68 → 255.255.255.255:67`) di una macchina appena accesa, bloccate dalla regola predefinita. Imparare a riconoscerlo serve a non perderci tempo.

Dopo il test ho disattivato la regola e verificato che il ping tornasse a funzionare.

## Un problema risolto dopo
La macchina attaccante non riusciva ad aggiornarsi. Il DHCP della rete isolata le indicava come gateway **sé stessa** (`default via <proprio indirizzo>`), quindi il traffico non arrivava mai al firewall. Ho impostato con `nmcli` un indirizzo fisso con gateway e DNS su pfSense.

## Cosa cerca un analista nei log del firewall
| Segnale | Possibile significato |
|---|---|
| Molti blocchi in entrata dallo stesso IP verso porte diverse | Scansione (T1595) |
| Un PC interno che contatta lo stesso IP esterno a intervalli regolari | **Beaconing** verso un server di comando e controllo (T1071) |
| Traffico in uscita su porte insolite | Malware o esfiltrazione |
| Modifiche alle regole del firewall | Qualcuno sta "aprendo le porte" |

<!-- Screenshot da aggiungere (ripuliti):
     - console di pfSense con WAN e LAN
     - regola di blocco ICMP nella pagina Firewall → Rules → LAN
     - log del firewall con le righe bloccate
     NON pubblicare il file config.xml: contiene l'hash della password e le chiavi private -->
