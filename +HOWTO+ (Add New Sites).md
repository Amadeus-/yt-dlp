# HOWTO — Add Support for a New Site (manual workflow)

This is the upstream `CONTRIBUTING.md > Adding support for a new site` quick-list, re-written for **this local checkout** at `C:\Dev\+YouTubeDownloader_(yt-dlp)+\` with the venv at `.\.venv\`. The original commands assume `hatch` resolves on `PATH` after a `hatch shell` — that's the contributor's normal flow. Here, we invoke everything via the venv's absolute python so nothing depends on activation persisting between terminal sessions.

**Prerequisites already on this system:**
- Git, configured for the `Amadeus-/yt-dlp` fork (origin) and `yt-dlp/yt-dlp` (upstream).
- Python ≥ 3.10 on `PATH`.
- The venv at `.\.venv\` with the **dev dependency group** installed (`ruff`, `autopep8`, `pytest`, `pre-commit`, etc.). If a fresh install is ever needed: `Set-Location "C:\Dev\+YouTubeDownloader_(yt-dlp)+"` then `& ".\.venv\Scripts\python.exe" -m devscripts.install_deps --include-group dev`.
- **`hatch` installed system-wide via `pipx`** (per `CONTRIBUTING.md:156` — hatch is intentionally outside the venv). On a fresh machine: `python -m pip install --user pipx`, then `python -m pipx ensurepath` (one-time PATH update; restart the shell), then `pipx install hatch`. After that, `hatch` resolves on `PATH` globally and the commands below work as-written.
  - **On this machine**, the install landed at `C:\Users\Andy\.local\bin\hatch.exe` (shim) backed by a per-tool venv at `C:\Users\Andy\pipx\venvs\hatch\`. The shim dir is on the user `PATH`.
  - **PATH-fallback for old shell windows:** if you ever get `hatch : The term 'hatch' is not recognized...` in a PowerShell window, that window was opened *before* `pipx ensurepath` ran and is still using the old PATH snapshot. Two options: open a fresh PowerShell window (clean fix), or invoke the absolute path in the current one: `& "C:\Users\Andy\.local\bin\hatch.exe" <args>`. Either works the same.

**Copyright caveat (verbatim from upstream):** make sure the site is **not dedicated to copyright infringement**. yt-dlp does not support such sites, and PRs adding them will be rejected.

---

## 1. Fork the repo on GitHub

Already done — `https://github.com/Amadeus-/yt-dlp` is your fork. Skip this step for any new-extractor work.

## 2. Check out the source

Already done — checkout is at `C:\Dev\+YouTubeDownloader_(yt-dlp)+\`. If you ever need to reclone:

```powershell
git clone https://github.com/Amadeus-/yt-dlp.git "C:\Dev\+YouTubeDownloader_(yt-dlp)+"
```

> **Note:** the upstream doc shows `git clone git@github.com:USER/yt-dlp.git` (SSH). HTTPS works too and doesn't require an SSH key on the machine.

## 3. Start a new git branch

```powershell
Set-Location "C:\Dev\+YouTubeDownloader_(yt-dlp)+"
git checkout master
git pull --ff-only origin master    # make sure master is current with origin first
git checkout -b yourextractor
```

> **Note:** also a good moment to sync from upstream first if the fork is behind: `git fetch upstream` then `git merge --ff-only upstream/master` then `git push origin master`, *before* branching. Check ahead/behind with `git rev-list --left-right --count origin/master...upstream/master`.

## 4. Create `yt_dlp\extractor\yourextractor.py` from this template

Save the following at `C:\Dev\+YouTubeDownloader_(yt-dlp)+\yt_dlp\extractor\yourextractor.py` (rename the file *and* the class to your service name):

```python
from .common import InfoExtractor


class YourExtractorIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?yourextractor\.com/watch/(?P<id>[0-9]+)'
    _TESTS = [{
        'url': 'https://yourextractor.com/watch/42',
        'md5': 'TODO: md5 sum of the first 10241 bytes of the video file (use --test)',
        'info_dict': {
            # For videos, only the 'id' and 'ext' fields are required to RUN the test:
            'id': '42',
            'ext': 'mp4',
            # Then if the test run fails, it will output the missing/incorrect fields.
            # Properties can be added as:
            # * A value, e.g.
            #     'title': 'Video title goes here',
            # * MD5 checksum; start the string with 'md5:', e.g.
            #     'description': 'md5:098f6bcd4621d373cade4e832627b4f6',
            # * A regular expression; start the string with 're:', e.g.
            #     'thumbnail': r're:https?://.*\.jpg$',
            # * A count of elements in a list; start the string with 'count:', e.g.
            #     'tags': 'count:10',
            # * Any Python type, e.g.
            #     'view_count': int,
        }
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # TODO more code goes here, for example ...
        title = self._html_search_regex(r'<h1>(.+?)</h1>', webpage, 'title')

        return {
            'id': video_id,
            'title': title,
            'description': self._og_search_description(webpage),
            'uploader': self._search_regex(r'<div[^>]+id="uploader"[^>]*>([^<]+)<', webpage, 'uploader', fatal=False),
            # TODO more properties (see yt_dlp/extractor/common.py)
        }
```

> **Note:** the class name **must end with `IE`** (the discovery system finds it by suffix). The file name doesn't have to match the class, but conventionally does.

## 5. Add an import in `yt_dlp\extractor\_extractors.py`

Open `C:\Dev\+YouTubeDownloader_(yt-dlp)+\yt_dlp\extractor\_extractors.py`, find the alphabetically-correct spot, and add the import.

> **Note (trailing-comma rule, verbatim from upstream):** when adding to a *parenthesized* import group, **the last import in the group must have a trailing comma** so the code formatter respects line-per-import. Skip the comma and `ruff` will reflow your group into a single line in step 9.

## 6. Run the extractor's tests

**Upstream wording (this works now that the dev deps are installed):**

```powershell
Set-Location "C:\Dev\+YouTubeDownloader_(yt-dlp)+"
hatch test YourExtractor
```

The test may fail at first — that's expected. The failure output prints the missing/incorrect fields you can copy back into `_TESTS[0]['info_dict']`. Re-run until it's green.

- **Multiple tests:** if `_TESTS` has more than one entry, they're named `YourExtractor`, `YourExtractor_1`, `YourExtractor_2`, …
- **`only_matching: True` tests** are URL-pattern-only and don't count in the numbered series.
- **Run all of them in one go:** `hatch test YourExtractor_all`.

**Alternatives that don't go through `hatch`** (both work, the dev install gave us pytest and the run_tests wrapper):

```powershell
# yt-dlp's wrapper — same naming semantics as `hatch test`
& ".\.venv\Scripts\python.exe" -m devscripts.run_tests YourExtractor

# Direct pytest invocation
& ".\.venv\Scripts\python.exe" -m pytest "test\test_download.py" -k YourExtractor
```

> **Note (auth-needing tests):** if a test needs login, create `test\local_parameters.json` with `usenetrc: true`, or `username`/`password`, or `cookiefile` / `cookiesfrombrowser`. See section "Tip" below.

## 7. Make sure there's at least one test

Even if every video the extractor handles is geo-blocked, private, or otherwise inaccessible to automated tests, **add a test entry with the `'skip'` key set** explaining why it can't run. Example:

```python
_TESTS = [{
    'url': 'https://yourextractor.com/private/42',
    'only_matching': True,
}, {
    'url': 'https://yourextractor.com/watch/42',
    'skip': 'Geo-blocked outside JP',
    'info_dict': {'id': '42', 'ext': 'mp4', 'title': 'Example'},
}]
```

## 8. Check `yt_dlp\extractor\common.py` for helper methods

Open `C:\Dev\+YouTubeDownloader_(yt-dlp)+\yt_dlp\extractor\common.py` and skim the helper methods + the [info-dict reference](yt_dlp/extractor/common.py#L119-L440). Common ones worth knowing:

- `self._download_webpage(url, video_id, ...)` — fetch + decode
- `self._download_json(url, video_id, ...)` — fetch + JSON-parse
- `self._html_search_regex(pattern, html, name, fatal=True)` — single-capture extract
- `self._search_regex(pattern, text, name, default=NO_DEFAULT, fatal=True)` — non-HTML variant
- `self._og_search_*(webpage)` — OpenGraph metadata helpers (title, description, thumbnail, etc.)
- `self._extract_m3u8_formats(url, video_id, 'mp4', ...)` — HLS manifest → formats
- `self._extract_mpd_formats(...)` — DASH manifest
- `traverse_obj(obj, ('path', 'into', 'json'), default=None, expected_type=...)` — defensive nested-key access (preferred over `.get().get()` chains per the upstream coding conventions)
- `int_or_none`, `float_or_none`, `url_or_none`, `unified_strdate`, `unified_timestamp`, `parse_filesize`, `parse_count`, `parse_resolution`, `parse_duration`, `parse_age_limit` — all live in `yt_dlp.utils`

> **Note (mandatory metafields):** the info dict you return must have `'id'` plus either `'url'` or `'formats'`. For adult content, `'age_limit'` is also mandatory.

## 9. Lint / format

**Upstream wording:**

```powershell
Set-Location "C:\Dev\+YouTubeDownloader_(yt-dlp)+"
hatch fmt --check
```

Use `hatch fmt` (no `--check`) to automatically fix what's fixable.

**The rule (verbatim):** *"Rules that the linter/formatter enforces should not be disabled with `# noqa` unless a maintainer requests it. The only exception allowed is for old/printf-style string formatting in GraphQL query templates (use `# noqa: UP031`)."*

**Alternatives without `hatch`** — `hatch fmt` is literally `ruff check` + `autopep8`, so:

```powershell
# Check only (CI-equivalent)
& ".\.venv\Scripts\ruff.exe" check .
& ".\.venv\Scripts\autopep8.exe" --diff --recursive yt_dlp

# Auto-fix
& ".\.venv\Scripts\ruff.exe" check --fix .
& ".\.venv\Scripts\autopep8.exe" --in-place --recursive yt_dlp
```

> **Note (yt-dlp style worth remembering):** single-quote strings, double-quote docstrings, soft line-limit 100 chars (hard 120), `fatal=False` on optional regex extracts, prefer relaxed HTML regexes (`<span[^>]+class="title"[^>]*>([^<]+)`) over brittle exact-match patterns (`<span class="title">(.*?)</span>`) — extractor patterns rot the moment the site touches its markup.

## 10. Python-version compatibility

Make sure your code runs on **CPython ≥ 3.10** and **PyPy ≥ 3.11**. No older Python support is needed.

> **Note:** this machine only has CPython locally — there's no PyPy here. For PyPy verification you're relying on upstream's CI matrix after you open the PR. Avoid CPython-only features (e.g. `match` statements pre-3.10 are fine; certain `dict | dict` merge edge-cases differ; `typing.Self` is 3.11+; etc.).

## 11. Commit and push

```powershell
Set-Location "C:\Dev\+YouTubeDownloader_(yt-dlp)+"
git add yt_dlp\extractor\_extractors.py
git add yt_dlp\extractor\yourextractor.py
git commit -m "[yourextractor] Add extractor"
git push origin yourextractor
```

> **Note (commit-message convention from observed git log):** the format is `[scope] Subject (#PR)`, where `scope` for a new extractor is the lowercase extractor name (without the `IE` suffix). After PR merge, the `(#PR)` part is appended by the merge tool. **Single-line subject is the norm**, optionally followed by a body — but most extractor commits are subject-only.

## 12. Open a pull request

Visit `https://github.com/Amadeus-/yt-dlp` in a browser. GitHub will show a "Compare & pull request" banner for the just-pushed `yourextractor` branch. Click it. Target branch is **upstream `yt-dlp/yt-dlp` master**.

Or via GitHub CLI if installed:

```powershell
gh pr create --base master --head yourextractor --repo yt-dlp/yt-dlp
```

> **Note:** filling out the issue/PR template is required upstream. Strip nothing — the template gates triage. Include `-vU` output for any failure-reproduction screenshots, and verify reproduction on **nightly** (`yt-dlp -U` then `--update-to nightly`) before filing.

---

## Tip — Tests that need authentication

If your extractor needs a login to retrieve any of its `_TESTS` URLs, create `C:\Dev\+YouTubeDownloader_(yt-dlp)+\test\local_parameters.json`:

```json
{
    "usenetrc": true
}
```

or with explicit credentials:

```json
{
    "username": "your user name",
    "password": "your password"
}
```

or pointing at a cookies file / browser:

```json
{
    "cookiefile": "C:\\path\\to\\cookies.txt"
}
```

```json
{
    "cookiesfrombrowser": ["firefox"]
}
```

> **Note:** `test\local_parameters.json` is **gitignored** — credentials in it won't accidentally be committed. Still, prefer `cookiesfrombrowser` or a `.netrc` over typing the password into a JSON file.

---

## Notes for manual work (concise observations)

- **Iterative dev without rebuilding `yt-dlp.exe`:** run yt-dlp directly from the source tree as `& ".\.venv\Scripts\python.exe" -m yt_dlp [ARGS]`. Code changes are picked up immediately on the next invocation. Only rebuild the exe when you actually want a fresh distributable binary (use the agent or follow the build steps in `YT-DLP-Expert.md`).
- **Editable install** (alternative to source-tree runs): `& ".\.venv\Scripts\python.exe" -m pip install -e ".[default,dev]"` — after this, `yt-dlp [ARGS]` works from the venv and reads source live. Idempotent; run it once per env.
- **Match-filter / format selector experimentation** doesn't need a new extractor — those are configurable per-invocation.
- **PR-merge churn:** upstream usually `squash-on-merge`. Don't sweat fixup commits during review; they'll collapse to one commit at merge time. Don't force-push your branch *during* review unless a maintainer asks — it makes review-thread navigation harder.
- **Pending-fixes label:** if a maintainer requests changes, the `pending-fixes` label gets applied. After you push fixes, ping the labeler if it isn't removed within a few days.
- **Don't touch `Changelog.md`** — it's auto-generated by `devscripts\make_changelog.py` from commit subjects + `devscripts\changelog_override.json`. Manual edits will conflict.
- **`hatch run setup`** installs a pre-commit hook that blocks commits with lint failures. Optional — if you find it intrusive, skip it; CI catches the same things at PR time. Add `--no-verify` to `git commit` if you've already installed it and want to override locally (don't push past it though).
- **`make_lazy_extractors.py` after adding a new extractor:** not strictly required for the test commands above to work, but if you rebuild `yt-dlp.exe` afterward, run it first so the exe knows about your new class without paying startup-time discovery. The agent's build flow handles this automatically.
- **Network-touching tests** can be flaky on transient host issues. If a test fails once intermittently, re-run before assuming a real regression.
