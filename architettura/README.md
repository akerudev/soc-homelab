# Architettura del laboratorio

## Schema
```
                         Internet
                            │
                     router di casa
                            │
                    Mac (hypervisor UTM)
                            │  rete "condivisa" (NAT)
                    ┌───────┴────────┐
                    │  pfSense (WAN) │
                    │    firewall    │
                    │  pfSense (LAN) │  .254 = gateway del dominio
                    └───────┬────────┘
                            │  rete isolata 192.168.128.0/24
       ┌────────────────────┼────────────────────┬───────────────┐
       │                    │                    │               │
  Domain controller     Client Windows 11     SIEM Wazuh      Attaccante
  Windows Server 2022   unito al dominio      Ubuntu 24.04    ParrotOS
  .200 (DNS, AD)        (DHCP)                .20             .10
       │                                         ▲
       └──── agente Wazuh: invia i log ──────────┘
```

Un secondo laboratorio, separato, gira su VirtualBox (Kali, Ubuntu Server, Ubuntu Desktop, Windows 11) ed è servito per le prime esercitazioni su traffico e log di Linux.

## Piano degli indirizzi (rete isolata)
| Indirizzo | Macchina | Ruolo |
|---|---|---|
| .1 | Mac | Host, usato per amministrare (browser, SSH) |
| .10 | ParrotOS | Simulazione delle attività dell'attaccante |
| .20 | Wazuh | SIEM: server, indexer, dashboard |
| .200 | Domain controller | Active Directory e DNS del dominio |
| .254 | pfSense (LAN) | Gateway e inoltro DNS verso Internet |

## Scelte di progetto
- **Rete isolata (Solo Host):** le simulazioni di attacco non escono mai dal laboratorio.
- **Il firewall come unica uscita:** tutto il traffico verso Internet passa da pfSense, quindi è registrabile e bloccabile.
- **Indirizzi fissi** per i server (domain controller, SIEM, firewall): gli agenti e i client devono trovarli sempre allo stesso posto.
- **Un account di servizio separato** per il SIEM: i servizi non girano con l'account di una persona che ha i permessi di amministratore (privilegio minimo).

<!-- Screenshot da aggiungere: elenco delle VM in UTM, senza nomi personali visibili -->
