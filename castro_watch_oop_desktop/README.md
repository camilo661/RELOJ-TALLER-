# CASTRO Watch OOP Desktop

This is a separate desktop project built with a stronger object-oriented and modular architecture.

## Structure

```text
castro_watch_oop_desktop/
|-- app.py
|-- backend/
|   |-- application/
|   |-- domain/
|   `-- infrastructure/
`-- frontend/
    `-- ui/
```

## Patterns Used

- `Singleton`: global `ClockEngineSingleton`
- `Factory`: `GeometryFactory` and `ApplicationBootstrapper`
- `Registry`: `ThemeRegistry`
- `Service`: `ClockStateMutator`, `BackgroundTicker`, and `ClockEngine`
- `Layered architecture`: backend and frontend split, with internal domain, application, infrastructure, and UI modules

## Run

```bash
python app.py
```
