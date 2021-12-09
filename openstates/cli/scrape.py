from pathlib import Path
from spatula.cli import scrape
from .people import merge
import click


@click.command()
@click.argument("abbr")
@click.argument("scraper_type")
def main(abbr: str, scraper_type: str):
    output_dir = Path(f"_scrapes/{abbr}/{scraper_type}")
    try:
        scrape([f"scrapers_next.{abbr}.{scraper_type}", "-o", output_dir, "--rmdir"])
    except SystemExit as e:
        if e.code != 0:
            raise
    merge([abbr, str(output_dir)])


if __name__ == "__main__":
    main()
