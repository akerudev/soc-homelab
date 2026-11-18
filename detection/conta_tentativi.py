import re
from collections import Counter

percorso = "dati/esempio-auth.log"

SOGLIA = 5

# Passo 1: leggere il file
with open(percorso) as f:
    righe = f.readlines()

print("Righe nel log:", len(righe))

# Passo 2: tenere solo i tentativi falliti
falliti = []
for riga in righe:
    if "Failed password" in riga:
        falliti.append(riga)

print("Tentativi falliti:", len(falliti))

# Passo 3: il modello per trovare l'IP
modello_ip = re.compile(r"from (\d+\.\d+\.\d+\.\d+)")

# Passo 4: contare i tentativi per IP
conteggio = Counter()
for riga in falliti:
    trovato = modello_ip.search(riga)
    if trovato:
        conteggio[trovato.group(1)] += 1

inesistenti = Counter ()
for riga in righe:
    trovato = modello_ip.search(riga)
    if trovato and "invalid user" in riga:
        inesistenti[trovato.group(1)] += 1

# Passo 6: quali IP sono riusciti ad entrare?
accettati = set()
for riga in righe:
    if "Accepted" in riga:
        trovato = modello_ip.search(riga)
        if trovato:
            accettati.add(trovato.group(1))
print()
for ip, n in conteggio.most_common():
    stato = ""
    if n >= SOGLIA and ip in accettati:
        stato = "🚨 CRITICO: brute force RIUSCITO"
    elif n >= SOGLIA:
        stato = "⚠️  ALERT: possibile brute force"
    elif inesistenti[ip] >= 3:
        stato = "⚠️  ALERT: possibile attacco con utenti non esistenti"
    print(f"{ip:15}  {n:3} tentativi  ({inesistenti[ip]} su utenti inesistenti ) {stato}")