##Erweiterungen für die Integration der Station "Maskenscanner" in die Plattform MusOS:

Im Projekt war eine Vorbereitung für die Integration der Station "Maskenscanner" gefordert, da die Stationen der "5 Units" an physisch unterschiedlichen Orten entwickelt wurden und somit ein Test mit laufender Station nicht möglich war. Bei der Insatallation im dann fertiggestellten Museum wird die Integration vorgenommen. Das heisst, in einer Zusammenfassungsstation können die besucher*innen sich das vom Maskenscanner erstellte Bild nochmals anzeigen lassen. 

Die Station Maskenscanner wurde erweitert, sodass dem zu speichernden Bild ein über eine URL zu beziehender Prefix dem Dateinamen hinzugefügt werden kann. Ebenso wurde implementiert, dass sämtliche erstellten Bilder nach einem Tag auf dem Rechner physisch gelöscht werden.

In den Maskenscanner wurd ein Raspberry Pi (analog der Stationen der ersten Iteration des Projekt-Moduls) integriert, der mittels der Python und Shell Scripts in diesem Verzeichnis als Beacon-Sensor, sowie als einfacher Rest-Server konfiguriert wird. Nähert sich eine Besucher\*in der Station, wird diese mittels dem mitgeführten Beacon registriert. Wird nun die Station mit dem Buzzer gestartet, kann die Station sich über den Rest-Service auf dem Raspberry Pi die aktuelle UUID des Besucher\*innen-Beacon geben lassen und diese dem Dateinamen des Bild beim Speichern als Prefix hinzufügen. 

Auf der Maskenscannerstation selbst wird ebenfalls ein Rest-Server mit einer API gestartet, über die der zentrale Server das zum jeweiligen Besucher\*innen-Beacon gehörende Bild von der Station laden kann. Dieses kann dann weiter in der Ausstellung in anderen Stationen genutzt werden. Für das Fasnachtsmuseum Schloss Langenstein wird das Bild an der Station "Besuchszusammenfassung" nochmals gezeigt. Datenschutzrechtlich ist die Speicherung bedenkenlos, da lediglich ein maskiertes Bild gezeigt wird (mit gerendertem Overlay). Die Bilder auf der Maskenstation werden nach einem Tag endgültig gelöscht. Der Server selbst persistiert das Bild nicht, sondern zeigt es lediglich on Demand über den Rest-Aufruf an. 


###Anwendung: 

In die Station "Maskenscanner" muss ein mit Raspberry Pi 3 oder 4 mit Raspberry Pi OS oder Ubuntu Mate integriert werden. Idealerweise im vorderen Bereich des Gehäuses und nicht durch andere Elektronik versteckt oder abgeschirmt (die Funksignale (BLE) müssen ungehindert empfangen werden können). 

Auf diesen Raspberry muss das Verzeichnis ".../sensors/beacons" aus diesem Repository kopiert werden.

Hier nun die Scripts "setup\_mask\_sensor.sh" sowie "start\_rest\_server.sh" starten. 

Die Scripts starten den Beacon-Sensor, einen leichtgewichtigen Rest-Server, bauen die Serverkommunikation auf, um die Beacon-Daten zu erhalten und auf Besucher\*innenaktionen reagieren zu können und ermöglichen dem Maskenscanner, die Identität des mitgeführten Beacons zu ermitteln. 

Auf den Rechner des Maskenscanners müssen die Scripts "getImageAPI.sh", sowie "start\_rest\_server.sh" aus dem Verzeichnis ".../sensors/beacons" kopiert werden. 

Anschliessend hier ebenfalls das Script "start\_rest\_server.sh" starten. 

Auf dem Server muss die URL des Maskenscanners mitgegeben werden. Diese kann als MusOS-Object in der Datenbank angelegt werden. 
Hierzu kann eine Datenbankverbindung zur MongoDB hergestellt und ein Object vom Type "REST Gateway" erstellt werden. 

Die Definition findet sich unter ".../data/types/typerestgateway.json":

 ``"definition": {
            "fieldsets": [
                {
                    "id": "general",
                    "name": "Allgemein",
                    "fields": [
                        {
                            "id": "name",
                            "name": "Name",
                            "type": "text",
                            "mandatory": true
                        },
                        {
                            "id": "url",
                            "name": "URL",
                            "type": "text",
                            "mandatory": true
                        },
                        {
                            "id": "protocol",
                            "name": "Protokoll",
                            "type": "select",
                            "options": ["http", "https"]
                        },
                        {
                            "id": "gatewayuser",
                            "name": "Benutzer",
                            "type": "text"
                        },
                        {
                            "id": "gatewaypassword",
                            "name": "Password",
                            "type": "password"
                        }
                    ]
                }``

Die Response dieses REST-Calls, also das erhaltene Bild, lässt sich schliesslich in den individuellen Stationen einbinden. 

##Erweiterung für die Integration der Station "Holzwand" des FNM Langenstein in die Plattform MusOS

Die Station "Interaktive Holzwand" aus dem ersten Teil des Projektmoduls verbindet die Technologien Projection-Mapping und leitfähige Tinte zu einer Quizstation, in dem Besucher\*innen einige einfache Fragen zum in der Ausstellung gelernten präsentiert bekommen. Die Station besiert in erster Linie aus ein grossen Holzplatte, auf die mit leitfähiger und Prints die Gestaltung aufgbracht wurde. 
Ein weiteres Ziel der Projektverlängerung in den "5 Units" war, diese Station in die Plattform MusOS zu integrieren. Diese Integration wurde hier vorbereitet, in dem an der Station ebenfalls ein Raspberry Pi installiert wird, der auch hier wiederum als Beacon-Sensor und als Rest-Server fungiert. Bei Annhärung wird die Besucher\*in registriert. Da es eine finite Anzahl von Auswahlmöglichkeiten und Fragen gibt (beides ist physisch fix mit der Holzwand verbunden), wird lediglich die Fragenummer und ob die Frage auf Anhieb richtig beantwortet wurde, auf den MusOS-Server übertragen. Diese Antworten können bei der Integration ins Museum ebenfalls auf einer Zusammenfassungsstation angezeigt werden. 

neue Files für Repo: 
data/type_restgateway.json
customer/data/type_woodwallrecap.json
/sensors/beacon













