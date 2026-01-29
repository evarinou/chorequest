# ChoreQuest - Entwicklungsfortschritt

## Phase 1: Backend-Grundgerüst [x]

- FastAPI App mit async SQLAlchemy + PostgreSQL 16
- Alle Models (User, Room, Task, TaskInstance, TaskCompletion, Achievement, UserAchievement, WeeklySummary)
- Pydantic v2 Schemas (Request/Response für alle Entities)
- CRUD Endpoints (Users, Rooms, Tasks, Instances)
- API-Key Bearer Token Authentifizierung
- Health + Dashboard Endpoints
- Leaderboard Endpoints
- Seed-Daten (Benutzer, Räume, Tasks, Achievements)
- Dockerfile + docker-compose.yml (Backend + PostgreSQL 16)
- Alembic vorbereitet

## Phase 2: Gamification-Logik [x]

- Punkteberechnung mit Raum-Multiplikator, Frühbonus (+20%), Streak-Bonus (+10%/+25%), Raum-Completion-Bonus (+50%)
- Streak-Tracking (aufeinanderfolgende Tage mit erledigten Tasks)
- Achievement-System mit automatischer Freischaltung
- 6 Basis-Achievements (Erste Schritte, Fleißig, Putz-Profi, Küchenheld, Streak-Master, Wochensieger)
- Achievement-Fortschritts-Endpoint
- APScheduler für tägliche Task-Instanz-Generierung und wöchentlichen Points-Reset
- User-Stats Endpoint (Completions, Lieblingsraum, Achievement-Anzahl)

## Phase 3: Home Assistant Integration [x]

- Custom Component mit Config Flow (Backend-URL + API-Key)
- Automatischer Raum-Sync aus HA-Areas
- Automatischer Benutzer-Sync aus HA-Person-Entities
- DataUpdateCoordinator mit 60s Polling
- Sensoren: Punkte pro User, Streak, Tasks heute, überfällige Tasks
- Binary Sensor: Überfällige Tasks vorhanden
- Todo-Listen: Eine pro Raum
- Services: complete_task, refresh_tasks, sync_rooms
- Periodischer Re-Sync alle 24h
- Webhook-System für Echtzeit-Benachrichtigungen (Backend → HA)

## Phase 4: SvelteKit Frontend [x]

- SvelteKit + TailwindCSS + @mdi/js
- Dashboard mit heutigen Aufgaben, gruppiert nach Raum
- Aufgaben-Verwaltung (CRUD für Task-Templates)
- Raum-Übersicht mit Point-Multiplier-Konfiguration
- Rangliste (Gesamt + Wöchentlich)
- Profil-Seite mit Statistiken und Achievements
- Dark Mode
- Mobile-First Design
- API-Client mit Auth-Handling

## Phase 5: Claude AI Integration [x]

- Claude Service mit wöchentlicher Zusammenfassung
- Stats-Sammlung (User, Raum, Achievements pro Woche)
- Fallback-Text wenn kein API-Key konfiguriert
- Task-Vorschläge basierend auf Erledigungshistorie
- Endpoints: Liste, Latest, Generate
- Scheduler-Integration (Sonntags automatisch)

## Phase 6: Feinschliff [aktuell]

- [x] Backend-Tests (pytest mit SQLite in-memory)
- [x] Webhook-System (Backend → Home Assistant, fire-and-forget)
- [x] README.md mit Setup-Anleitung
- [ ] Initiale Alembic-Migration
- [ ] Mobile-Optimierung Frontend
- [ ] Error Handling Verbesserungen
