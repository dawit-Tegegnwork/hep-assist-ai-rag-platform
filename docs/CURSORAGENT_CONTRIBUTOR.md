# cursoragent contributor — status

## Current state (2026-06-29)

- GitHub **Contributors API** for all six pinned repos returns only `dawit-Tegegnwork`.
- Commit history was rewritten and force-pushed to remove `Co-authored-by: Cursor <cursoragent@cursor.com>`.
- The repo sidebar may still show **cursoragent** for 24–72 hours while GitHub refreshes contributor cache.

## If sidebar still shows cursoragent after 72 hours

1. Open **Insights → Contributors** on the repo — if only you appear, the sidebar is stale UI.
2. Contact [GitHub Support](https://support.github.com/) or post in [GitHub Community](https://github.com/orgs/community/discussions) to request contributor cache refresh.
3. There is no self-serve “remove contributor” button.

## Prevention

Never add this line to commit messages:

```
Co-authored-by: Cursor <cursoragent@cursor.com>
```

All future commits from this portfolio work use author **dawit-Tegegnwork** only.
