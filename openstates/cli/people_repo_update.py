import datetime
import os
import typing

import requests
import logging
import shutil

from pathlib import Path

import click
import git

from ..cli.committees import to_database as committee_to_database
from ..cli.people import to_database as people_to_database

logger = logging.getLogger(__name__)


def is_recent_people_repo_commit() -> bool:
    repo_url = "https://api.github.com/repos/openstates/people/commits"
    response = requests.get(repo_url)
    recent_commit_exists = False
    if response.status_code == 200:
        latest_commit = response.json()[0]
        last_commit_time = latest_commit["commit"]["committer"]["date"]
        # Ensure it's UTC-aware
        last_commit_time = datetime.datetime.fromisoformat(
            last_commit_time.rstrip("Z")
        ).replace(tzinfo=datetime.timezone.utc)
        two_hours_ago = datetime.datetime.now(
            datetime.timezone.utc
        ) - datetime.timedelta(
            minutes=2 * 60 + 5
        )  # 2 hours and 5-minute buffer.
        recent_commit_exists = last_commit_time > two_hours_ago
    return recent_commit_exists


def clone_people_repo() -> None:
    repo_name = "people"
    data_path = "data"
    base_dir = (
        Path(os.environ["OS_PEOPLE_DIRECTORY"])
        if "OS_PEOPLE_DIRECTORY" in os.environ
        else Path(".")
    )
    # This is mostly for local development
    if (base_dir / data_path).is_dir():
        logger.info(f"{repo_name} directory exist")
        return

    logger.info(f"Cloning {repo_name}")
    git.refresh("/usr/bin/git")
    repo_url_ssh = "git@github.com:openstates/people.git"
    git.Repo.clone_from(repo_url_ssh, repo_name)
    logger.info(f"Done cloning {repo_name}!")

    current_directory = base_dir / repo_name
    source_data_dir = current_directory / data_path
    destination_data_dir = base_dir / data_path
    shutil.copytree(source_data_dir, destination_data_dir)


def get_keyword_args(keyword_args: list) -> dict:
    def parse_value(value: str) -> typing.Union[bool, str]:
        if value.lower() == "true":
            return True
        elif value.lower() == "false" or value.lower() == " " or value.lower() == "":
            return False
        return value

    keyword_dict = {
        k: parse_value(v) for item in keyword_args for k, v in [item.split("=")]
    }
    return keyword_dict


@click.group()
def main() -> None:
    pass


@main.command()
@click.argument("other-options", nargs=-1)
@click.option(
    "--purge/--no-purge",
    default=False,
    help="Set to True to purge data no in repo from database.",
)
@click.option(
    "--force-ingest/--no-force-ingest",
    default=False,
    help="Force ingest of data to database.",
)
@click.option(
    "--people/--no-people",
    default=False,
    help="Set to True to ingest only people.",
)
@click.option(
    "--committees/--no-committees",
    default=False,
    help="Set to True to ingest only people.",
)
@click.pass_context
def update(
    ctx: typing.Any,
    other_options: list[str],
    purge: bool,
    force_ingest: bool,
    people: bool,
    committees: bool,
) -> int:

    keyword_args_dict = get_keyword_args(other_options)

    abbreviation = keyword_args_dict.get("abbreviation", None)
    purge = purge or keyword_args_dict.get("purge", False)
    force_ingest = force_ingest or keyword_args_dict.get("force-ingest", False)
    people = people or keyword_args_dict.get("people", False)
    committees = committees or keyword_args_dict.get("committees", False)

    if not force_ingest:
        logger.info("Checking if an update is necessary")
        if not is_recent_people_repo_commit():
            logger.info(
                "There was no recent update to Openstates People Repo \n exiting..."
            )
            return 0

    logger.info(
        "An update is necessary...\nBegin updating Openstates People to-database!"
    )

    clone_people_repo()

    abbreviations = [abbreviation] if abbreviation else []

    if people and not committees:
        ctx.invoke(people_to_database, abbreviations=abbreviations, purge=purge)
    elif committees and not people:
        ctx.invoke(committee_to_database, abbreviations=abbreviations, purge=purge)
    else:
        ctx.invoke(people_to_database, abbreviations=abbreviations, purge=purge)
        ctx.invoke(committee_to_database, abbreviations=abbreviations, purge=purge)
    return 0


if __name__ == "__main__":
    main()
