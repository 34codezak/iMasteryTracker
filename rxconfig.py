import reflex as rx


class Rxconfig(rx.Config):
    app_name = "imasterytracker"
    db_url = "sqlite:///imsterytracker.db"
    env: str = "dev"
    port: int = 8000
    disable_plugins = ["reflex.plugins.sitemap.SitemapPlugin"]


config = Rxconfig (app_name="imasterytracker")
