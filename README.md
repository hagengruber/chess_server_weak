# chess_server_weak
Dieses Repository stellt im Rahmen der Projektarbeit im Fach **Sichere Programmierung** das Projekt **chess_server** in der schwachen Version zur Verfügung.

## Getting started
### Prerequisites
Die benötigten Packages von der _requirements.txt_ Datei installieren:

- ```pip install -r requirements.txt```


## Usage
### Allgemein
Um das Projekt zu benutzen, muss man den Server starten und sich dann mit einem Client via TCP verbinden.
### Server
Um den Server zu starten, muss lediglich die Datei _main.py_ ausgeführt werden:
- ```python3 ./main.py```

Dadurch startet der Server automatisch mit der verwendeten IP-Adresse auf dem Port **8080**


### Client
Um nun eine Verbindung mit dem Server zu erstellen, verbindet man sich mit Telnet:
- ```telnet IP_SERVER 8080```

Es wird empfohlen, als Betriebssystem Linux zu verwenden, da die einwandfreie Darstellung der Anwendung ansonsten nicht gewährleistet werden kann