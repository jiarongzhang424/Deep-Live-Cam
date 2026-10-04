# Always on information monitor

This small GitHub Actions workflow checks GitHub release feeds and, when an X API credential is supplied, X recent search. It writes links to a GitHub Issue for review. No browser session, Cookie, personal account password, or paid search service is stored in this repository.

The workflow runs at 01:17 and 13:17 UTC each day (09:17 and 21:17 China time) while GitHub Actions is enabled on the repository's default branch. It can also be run manually from the Actions tab. Schedules may be delayed, and inactive public repositories can have scheduled workflows disabled by GitHub.

## Configure

1. Put this repository's files on the default branch, enable GitHub Actions, and permit the workflow to write Issues.
2. Optionally add `X_BEARER_TOKEN` as a repository Actions secret. Alternatively add `X_API_KEY` and `X_API_SECRET` for an app token. These are **X developer API credentials**, not the `auth_token`/`ct0` browser Cookies. X recent search access and pricing depend on the X developer plan. Without these secrets, X is skipped and GitHub releases still run.
3. Edit `config.json` to change the X search, release feeds, keywords, or maximum results. No secret belongs in this file.
4. Trigger **Information monitor** once from Actions and inspect its run log and resulting Issue before relying on the schedule. This monitor lives in `tools/always-on-monitor/` within the Deep-Live-Cam repository.

The workflow uses GitHub's automatically issued `GITHUB_TOKEN`; do not copy a personal access token into the repository. Each item is only a lead for review. The workflow does not make Codex learn permanently or execute changes on its own. The included Codex skill describes how to review a digest during a later authorized task.

## Local check

`python -m py_compile tools/always-on-monitor/monitor.py` checks syntax without contacting any service. A full run needs the repository context and GitHub token. The cloud environment's files and secrets do not automatically follow a new task; GitHub preserves the code, and each cloud environment must have its own approved credentials.
