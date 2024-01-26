Release Process:

* bump version in `pyproject.toml`
* update `CHANGELOG.md`
* once code is merged into `main`
  * Create a new Release in Github
    * Target `main`
    * Create a new tag that matches new version from `pyproject.toml`
  * By creating a tag, this triggers the [release workflow](./.github/workflows/release.yml) which builds and
    pushes the new version to PyPi

Post-Release updates:

* api-v3
* openstates.org
* scrapers
* people
