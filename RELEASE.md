# Release instructions

## Release Process:

* bump version in `pyproject.toml`
* update `CHANGELOG.md`
* once code is merged into `main`
    * Create a new Release in Github
        * Target `main`
        * Create a new tag that matches new version from `pyproject.toml`
    * By creating a tag, this triggers the [release workflow](./.github/workflows/release.yml) which builds and
      pushes the new version to PyPi

## Post-release steps

### **Mandatory** Post-Release updates:

Because openstates-core is used by several other openstates repositories as a dependency,
there is functionality that couples changes in this repo to the other repo. After releasing
an update to this repo, you MUST bump up the version of the `openstates` dependency and
perform release steps for the following:

* openstates-scrapers: simply merge a PR against the `main` branch
*
openstates-realtime: [follow deploy steps](https://github.com/openstates/openstates-realtime?tab=readme-ov-file#deployment)

### **Suggested** Post-Release updates:

If you make a change to the data models (outside of scrape-specific models), then you
probably need to bump one or more of the following so that they continue to query
the data correctly:

* api-v3
* openstates.org

Less frequently, the following need to be updated

* people
* openstates-geo

### Useful commands

To assess the `openstates-core` version of multiple Open States repositories, if they are
all checked out in the same directory on your machine:

`grep -Hrn --include="pyproject.toml" "openstates =" .`
