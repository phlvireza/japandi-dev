
## Hermes development workflow

- Work in /workspace/japandi-dev on branch qa.
- Read README.md and applicable nested instructions before editing.
- Preserve existing unrelated changes.
- For editing tasks, fetch origin and fast-forward qa before starting.
- Edit generator inputs under _src instead of generated HTML.
- Run python3 -B build.py after changing generator inputs.
- Before committing website changes, run:
  - python3 -B build.py --check
  - python3 -B -m unittest discover -s tests -q
- Review the diff and commit only files related to the requested task.
- Push requested changes to origin qa for staging deployment.
- Never push to main, merge production PRs, force-push, or delete branches.
- The human owner promotes QA changes to production through a PR.
- Change infrastructure, workflows, or credentials only when explicitly requested.
- Never expose credentials or read private key contents.
- Report changed files, validation results, commit SHA, and staging URL.
- Verify deployment results before claiming deployment succeeded.
