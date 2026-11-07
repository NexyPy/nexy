# Nexy-Tutorial: Erstellen Sie Schritt für Schritt eine Notizen-App

Das Nexy-Tutorial erstellt eine Notizen-App aus einem leeren Ordner zu einem Produktions-Build, einen Teil nach dem anderen, und jeder Teil endet mit einer App, die ausgeführt wird.

Neu bei Nexy? Der [Schnellstart](quick-start.md) zeigt, dass es in drei Minuten läuft; Kommen Sie hierher zurück, um zu erfahren, wie es funktioniert.

## So funktioniert das Tutorial

- **Eine App, die wächst.** Jeder Teil fügt der Notizen-App des vorherigen Teils eine Funktion hinzu.
- **Ihr Router.** Die Teile folgen dem oben im Menü ausgewählten Router: dateibasiert, modular oder benutzerdefiniert. Schalten Sie es dort um, und die Dateien jedes Teils ändern sich damit.
- **Code, der ausgeführt wird.** Jede Datei mit einem Namen darüber ist eine ganze Datei, und die Testsuite spielt die Teile der Reihe nach in einem neuen Projekt ab: Was Sie kopieren, wird ausgeführt.
- **Stoppen Sie irgendwo.** Jeder Teil dauert 10 bis 20 Minuten und endet mit dem, was im Browser überprüft werden muss.

## Die Teile

### Einheit 1: Die Grundlagen

| Teil | Was Sie hinzufügen | Was Sie lernen |
|---|---|---|
| [1. Erstellen Sie das Projekt](../tutorial/create-the-project.md) | ein Projekt, das läuft | `nexy new`, `nexy dev` |
| [2. Seiten und Layouts](../tutorial/pages-and-layouts.md) | die Notizenseite | Seiten, Ansichten, das Layout |
| [3. Dynamische Routen und eine API](../tutorial/dynamic-routes.md) | `/notes/1` und `/api/notes` | URL-Segmente, JSON-Routen, `notFound` |
| [4. Komponenten](../tutorial/components.md) | eine Karte pro Banknote | `.nexy` Komponenten und ihre Requisiten |

### Einheit 2: Daten

| Teil | Was Sie hinzufügen | Was Sie lernen |
|---|---|---|
| [5. Speichern Sie die Notizen in SQLite](../tutorial/store-the-notes.md) | ein Modell, eine Migration, ein Samen | SQLModel, `nx migrate` |
| [6. Erstellen Sie eine Notiz aus einem Formular](../tutorial/create-a-note.md) | ein Formular, das eine Notiz speichert | Aktionen, Formulare ohne JavaScript |
| [7. Validierungsfehler anzeigen](../tutorial/validation-errors.md) | eine Nachricht über dem Formular | Regeln in einer Aktion, `303`, `useSearchParams` |
| [8. Bearbeiten und löschen Sie eine Notiz](../tutorial/edit-and-delete.md) | die Formen einer Notiz | mehrere Aktionen pro Seite, versteckte Felder |
| [9. Paginieren Sie die Notizen](../tutorial/paginate-the-notes.md) | fünf Notizen pro Seite | `offset` und `limit`, Links zwischen Seiten |

### Einheit 3: Benutzer

| Teil | Was Sie hinzufügen | Was Sie lernen |
|---|---|---|
| [10. Erstellen Sie ein Konto und melden Sie sich an](../tutorial/accounts.md) | anmelden, anmelden, abmelden | Sitzungen, Passwort-Hashing |
| [11. Geben Sie jedem Benutzer seine eigenen Notizen](../tutorial/own-notes.md) | Notizen, die einem Benutzer gehören | Fremdschlüssel, `redirect`, `401` |
| [12. Setzen Sie ein vergessenes Passwort per E-Mail zurück](../tutorial/password-reset.md) | ein per E-Mail verschickter Reset-Link | `smtplib`, signierte Token, die ablaufen |

### Einheit 4: Interaktivität

| Teil | Was Sie hinzufügen | Was Sie lernen |
|---|---|---|
| [13. Durchsuchen Sie die Notizen während der Eingabe](../tutorial/search-the-notes.md) | ein Suchfeld, das während der Eingabe filtert | React Inseln, Requisiten von Python |
| [14. Markieren Sie eine Notiz, ohne die Seite neu zu laden](../tutorial/tick-a-note.md) | eine Schaltfläche „Fertig“ auf jeder Notiz | progressive Verbesserung, eine Aktion für ein Formular und für `fetch` |

### Kommt als nächstes

| Einheit | Was die App gewinnt |
|---|---|
| 5. Über die Anfrage hinaus | per E-Mail im Hintergrund geteilte Notizen, eine tägliche Übersicht, Live-Updates |
| 6. Schiff | Tests, Fehlerseiten und Protokolle, Sicherheitsheader, ein Docker Build |

## Nächste Schritte

- [Teil 1: Projekt erstellen](../tutorial/create-the-project.md)
- [Kernkonzepte](core-concepts.md): die im Tutorial verwendeten Wörter
