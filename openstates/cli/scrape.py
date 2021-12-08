from spatula.cli import scrape
from .people import merge
import click


@click.command()
@click.argument("abbr")
@click.argument("scraper_type")
def main(abbr: str, scraper_type: str):
    output_dir = f"_scrapes/{abbr}/{scraper_type}"
    scrape([f"scrapers_next.{abbr}.{scraper_type}", "-o", output_dir])
    if scraper_type == "people":
        merge([abbr, output_dir])


if __name__ == "__main__":
    main()
