from pathlib import Path
from spatula.cli import scrape
from .people import merge
import click


@click.command()
@click.argument("abbr")
@click.argument("scraper_type")
@click.option("--scrape-only/--no-scrape-only", help="Only perform scrape.")
@click.option("--merge-only/--no-merge-only", help="Only perform merge.")
def main(abbr: str, scraper_type: str, scrape_only: bool, merge_only: bool):
    output_dir = Path(f"_scrapes/{abbr}/{scraper_type}")
    if not merge_only:
        try:
            scrape(
                [f"scrapers_next.{abbr}.{scraper_type}", "-o", output_dir, "--rmdir"]
            )
        except SystemExit as e:
            if e.code != 0:
                raise
    if not scrape_only:
        merge([abbr, str(output_dir)])


if __name__ == "__main__":
    main()
