"""Application entry point for the OOP desktop edition of CASTRO Watch."""

from backend.application.bootstrap import ApplicationBootstrapper


def main() -> None:
    application = ApplicationBootstrapper().build()
    application.run()


if __name__ == "__main__":
    main()
