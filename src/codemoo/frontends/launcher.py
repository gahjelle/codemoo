"""Thin entry point: shows the splash screen, then hands off to cyclopts in tui.py."""

from codemoo.frontends.splash import SplashApp


def code_app_w_splash() -> None:
    """Show splash while imports load, then delegate to the tui cyclopts app."""
    SplashApp().run()

    from codemoo.frontends.tui import code_app  # noqa: PLC0415

    code_app()


def business_app_w_splash() -> None:
    """Show splash while imports load, then delegate to the tui cyclopts app."""
    SplashApp().run()

    from codemoo.frontends.tui import business_app  # noqa: PLC0415

    business_app()
