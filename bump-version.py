"""Bump the version of this package."""

import logging
import os
import re
import subprocess
from typing import TYPE_CHECKING, Any

import git
from bumpversion.bump import do_bump, get_next_version
from bumpversion.config import get_configuration
from bumpversion.config.files import find_config_file
from bumpversion.context import get_context
from bumpversion.ui import setup_logging
from bumpversion.versioning.models import Version

if TYPE_CHECKING:
    from bumpversion.config import Config


def is_final_version(version: Version | str, config: "Config") -> bool:
    """Check if the version is a final version (i.e., not a pre-release or build version).

    Args:
    -----
        version (Version | str): The version to check.
        config (Config): The configuration object.

    Returns:
    --------
        bool: True if the version is a final version, False otherwise.
    """
    if isinstance(version, Version):
        version = config.version_config.serialize(version)

    # If the version string matches X.X.X format, return True
    if re.match(r"^\d+\.\d+\.\d+$", version):
        return True
    # If 'final' in the version string, return True
    elif "final" in version:
        return True
    else:
        return False


def is_rebasing() -> bool:
    """Check if we are currently rebasing."""
    git_dir = subprocess.run(
        ["git", "rev-parse", "--git-dir"], capture_output=True, text=True
    ).stdout.strip()
    if not git_dir:
        return False
    return any("rebase" in entry for entry in os.listdir(git_dir))


def is_merging() -> bool:
    """Check if we are currently merging."""
    result = subprocess.run(
        ["git", "rev-list", "-1", "MERGE_HEAD"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return (
        result.returncode != 128
    )  # 128 means that the file does not exist, therefore we are not merging


def get_head_commit() -> str:
    """Get the commit hash of the HEAD.

    Returns:
    --------
        str: The commit hash of the HEAD
    """
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    )
    return result.stdout.strip()


def already_bumped() -> bool:
    """Check if the version has already been bumped."""
    git_log = subprocess.run(
        ["git", "log", "--pretty=%B ", "-1"], capture_output=True, text=True
    ).stdout
    return "Bump version" in git_log


def current_branch() -> str:
    """Get the current branch name."""
    return git.Repo(os.getcwd()).active_branch.name


def in_next_version_patch_branch(next_version: str) -> bool:
    """Check if we are in a the next version's patch release git branch.

    Args:
    -----
        next_version (str): The next version to check.

    Returns:
    --------
        bool: True if we are in a the next version's release branch, False otherwise
    """
    current_branch_no_v = current_branch().replace("v", "")
    return current_branch_no_v in next_version  # e.g. "1.2.3.dev5" in "1.2.3.dev"
    next_version_no_dev_or_post = ".".join(next_version.split(".")[:3])
    return current_branch_no_v == next_version_no_dev_or_post


def bump(type: str, **kwargs: dict[str, Any]) -> None:
    """Bump the version of this package.

    Args:
    -----
        type (str): The part of the version to bump. One of "major", "minor", "patch", "build", "prerelease", "postrelease".
        **kwargs (dict): Additional arguments to pass to the bump
    """
    # Setup the logging
    setup_logging(2)
    logger = logging.getLogger("bumpversion")
    logger.setLevel(logging.DEBUG)

    # Get the bump-my-version config
    found_config_file = find_config_file()
    config = get_configuration(found_config_file, **kwargs)
    config.tag = kwargs.get("dry_run", False)

    # Get the expected next version
    ctx = get_context(config)
    current_version = config.version_config.parse(config.current_version)
    next_version = get_next_version(
        current_version=current_version,
        config=config,
        version_part=type,
        new_version=None,
    )
    next_version_str = config.version_config.serialize(next_version, ctx)
    logger.debug(
        f"Current version: {config.current_version}, Expected next version: {next_version_str}"
    )

    # If 'post' is in the next version, then don't allow
    if "post" in next_version_str:
        raise RuntimeError(
            "Cannot bump version to a post-release version. Please develop on new patch dev release instead."
        )

    # Check to see if the type is valid
    if type not in config.parts.keys():
        raise ValueError(f"Invalid type: {type}")

    if is_merging():
        raise RuntimeError("Cannot bump version while merging.")
    elif is_rebasing():
        raise RuntimeError("Cannot bump version while rebasing.")
    # elif already_bumped() and not kwargs.get("force", False):
    #     raise RuntimeError(
    #         "Cannot bump version if it has already been bumped. To force bumping, use the --force flag."
    #     )
    elif (
        not in_next_version_patch_branch(next_version_str)
        and not is_final_version(next_version_str, config)
    ) and not kwargs.get("force", False):
        raise RuntimeError(
            f"Cannot bump a dev version on a branch other than the version's patch release branch (current branch is `{current_branch()}`, next version is '{next_version_str}'). To force bumping, use the --force flag."
        )
    elif (
        is_final_version(next_version_str, config) and not current_branch() == "master"
    ) and not kwargs.get("force", False):
        raise RuntimeError(
            f"Cannot bump version to a final version on a non-master branch. (current branch is `{current_branch()}`, next version is: '{next_version_str}'). To force bumping, use the --force flag."
        )
    else:
        # Bump the version
        do_bump(
            version_part=type,
            new_version=None,
            config=config,
            dry_run=kwargs.get("dry_run", False),
            config_file=found_config_file,
        )

    if kwargs.get("dry_run", False):
        # If dry run, print that is was a dry run for the user
        print("\n\nDry run complete. No changes were made.")


if __name__ == "__main__":
    import fire

    fire.Fire()
