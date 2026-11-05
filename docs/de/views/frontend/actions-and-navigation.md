# Aktionen und Navigation

Die Interaktion in Nexy wird über ein einheitliches System von **Aktionen** und **Navigation** abgewickelt, wodurch sichergestellt wird, dass Frontend und Backend ohne manuellen API-Glue-Code synchron bleiben.

## Der Aktionsvertrag

Eine **Aktion** ist eine serverseitige Funktion, die eine Mutation verarbeitet (z. B. das Aktualisieren einer Datenbank). 

1.  **Typisierte Eingabe**: Aktionen werden in Python mit Typhinweisen definiert. Nexy generiert einen passenden TypeScript-Client, sodass Sie in Ihrer IDE eine automatische Vervollständigung und Validierung erhalten.
2.  **Atomare Ausführung**: Eine Aktion ist eine einzelne `POST` Anfrage.
3.  **Ergebnisverarbeitung**: Aktionen geben ein typisiertes Ergebnis zurück, das der Client zum Aktualisieren der Benutzeroberfläche verwenden kann.

## Clientseitige Navigation

Die Navigation in Nexy ist „intelligent“. Anstelle eines vollständigen Neuladens des Browsers tauscht Nexy den Inhalt der aktuellen Seite aus, während die aktiven Layouts weiterhin bereitgestellt bleiben.

- **Die `Link`-Komponente**: Verwenden Sie die Framework-spezifische `Link`-Komponente, um clientseitige Übergänge durchzuführen.
- **Programmatische Navigation**: Verwenden Sie die Funktion `navigate()` von `@nexy/client`, um Seiten als Reaktion auf die Logik zu wechseln (z. B. nach einer erfolgreichen Anmeldung).

## Koordination: Aktion → Navigation

Das häufigste Muster besteht darin, eine Aktion auszuführen und den Benutzer dann zu einer neuen Seite zu navigieren.

**Der Revalidierungsablauf:**
1.  Der Client ruft eine Aktion auf.
2.  Die Aktion wird auf dem Server ausgeführt und ruft `revalidate("/path")` auf.
3.  Der Server gibt das Ergebnis zusammen mit einem Signal zum Aktualisieren des angegebenen Pfads zurück.
4.  Der Client aktualisiert den Seiteninhalt, um den neuen Status widerzuspiegeln.

## Framework-Implementierung

Die API zum Aufrufen von Aktionen und Navigieren variiert je nach Framework. Sehen Sie sich den Leitfaden **Unterschiede** für die von Ihnen gewählte Technologie an:

- [React Unterschiede](../react/differences.md)
- [Vue Unterschiede](../vue/differences.md)
- [Svelte Unterschiede](../svelte/differences.md)
- [Solid Unterschiede](../solid/differences.md)
- [Preact Unterschiede](../preact/differences.md)
