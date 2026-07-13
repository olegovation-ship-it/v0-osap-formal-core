from __future__ import annotations

import argparse
import shlex
import sys

from rc1_tag_release_lib import (
    CANDIDATE_TAG,
    CLOSURE_MERGE_COMMIT,
    FINAL_TAG,
    IMMUTABLE_TAG,
    IMMUTABLE_TAG_TARGET,
    git,
    local_tag_exists,
    origin_matches_repository,
    remote_tag_target,
    repository_root,
    worktree_is_clean,
)

ROOT = repository_root()
MESSAGE = ROOT / "release/v1.3.0/RC1_ANNOTATED_TAG_MESSAGE.txt"


def fail(message: str) -> None:
    raise SystemExit(f"RC1 annotated-tag creation refused: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create the authorized V0 OSAP v1.3.0-rc1 annotated tag. Dry-run by default."
    )
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--confirm-target")
    args = parser.parse_args()

    if args.push and not args.execute:
        fail("--push requires --execute")
    if args.execute and args.confirm_target != CLOSURE_MERGE_COMMIT:
        fail(f"--confirm-target must equal {CLOSURE_MERGE_COMMIT}")
    if not origin_matches_repository(args.remote):
        fail(f"remote {args.remote} does not resolve to the authorized repository")
    if not worktree_is_clean():
        fail("worktree is not clean")
    if local_tag_exists(CANDIDATE_TAG):
        fail(f"local tag {CANDIDATE_TAG} already exists")
    if local_tag_exists(FINAL_TAG):
        fail(f"final tag {FINAL_TAG} already exists")
    if remote_tag_target(args.remote, CANDIDATE_TAG):
        fail(f"remote tag {CANDIDATE_TAG} already exists")
    if remote_tag_target(args.remote, FINAL_TAG):
        fail(f"remote final tag {FINAL_TAG} already exists")
    if not local_tag_exists(IMMUTABLE_TAG):
        fail(f"historical tag {IMMUTABLE_TAG} is unavailable")
    historical = git("rev-list", "-n", "1", IMMUTABLE_TAG).stdout.strip()
    if historical != IMMUTABLE_TAG_TARGET:
        fail("historical v1.2.0 tag target changed")
    if not MESSAGE.is_file():
        fail("approved annotated-tag message is missing")

    verify_command = [sys.executable, "scripts/verify_rc1_tag_authorization.py", "--require-tags"]
    create_command = [
        "git",
        "tag",
        "-a",
        CANDIDATE_TAG,
        CLOSURE_MERGE_COMMIT,
        "-F",
        str(MESSAGE.relative_to(ROOT)),
    ]
    push_command = ["git", "push", args.remote, f"refs/tags/{CANDIDATE_TAG}"]

    if not args.execute:
        print("DRY RUN: no tag was created.")
        print("Verification:")
        print("  " + shlex.join(verify_command))
        print("Authorized annotated-tag command:")
        print("  " + shlex.join(create_command))
        print("Optional push command:")
        print("  " + shlex.join(push_command))
        print(f"Required explicit target confirmation: {CLOSURE_MERGE_COMMIT}")
        return 0

    verification = __import__("subprocess").run(verify_command, cwd=ROOT, text=True)
    if verification.returncode != 0:
        fail("authorization verifier failed")

    result = git(
        "tag",
        "-a",
        CANDIDATE_TAG,
        CLOSURE_MERGE_COMMIT,
        "-F",
        str(MESSAGE.relative_to(ROOT)),
        check=False,
    )
    if result.returncode != 0:
        fail(result.stderr.strip() or "git tag failed")

    resolved = git("rev-list", "-n", "1", CANDIDATE_TAG).stdout.strip()
    if resolved != CLOSURE_MERGE_COMMIT:
        fail(f"created tag resolves to {resolved}, expected {CLOSURE_MERGE_COMMIT}")

    print(f"PASS: created annotated tag {CANDIDATE_TAG} at {resolved}.")
    if args.push:
        pushed = git("push", args.remote, f"refs/tags/{CANDIDATE_TAG}", check=False)
        if pushed.returncode != 0:
            fail(pushed.stderr.strip() or "tag push failed")
        remote_target = remote_tag_target(args.remote, CANDIDATE_TAG)
        if remote_target != CLOSURE_MERGE_COMMIT:
            fail(f"remote tag resolves to {remote_target}, expected {CLOSURE_MERGE_COMMIT}")
        print(f"PASS: pushed {CANDIDATE_TAG} to {args.remote} and verified the exact target.")
    else:
        print("Tag remains local. Re-run with --execute --push and the same --confirm-target to publish it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
