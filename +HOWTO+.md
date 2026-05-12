# yt-dlp HOWTO

Quick-reference cheatsheet for everyday downloading.

**How to run:** open PowerShell here (or wherever `yt-dlp.exe` is on `PATH`) and use the commands below. `yt-dlp.conf` in this folder is auto-loaded — you don't need to repeat its defaults on the command line.

**What the config already provides** (so you don't need to pass these):

- `-t mp4` — H.264 + AAC inside an MP4 container, max compatibility
- `--js-runtimes node` — uses Node.js for YouTube's signature/n-sig challenges
- `--cookies-from-browser firefox` — sends Firefox cookies (avoids YouTube 403s)
- `--socket-timeout 30`, `--retries 15`, `--fragment-retries 15` — sensible network resilience
- `-N 4` — 4 concurrent fragment downloads (fast, but can cause 429s on non-YouTube sites — see [Troubleshooting](#troubleshooting))

---

## Quick links

- [Update yt-dlp](#update-yt-dlp)
- [Simple video download](#simple-video-download)
- [Quality / resolution](#quality--resolution) ← read this before downloading anything above 1080p
- [Audio only](#audio-only)
- [Playlists](#playlists)
- [Subtitles](#subtitles)
- [Trim / clip / sections](#trim--clip--sections)
- [SponsorBlock](#sponsorblock-youtube-only) (YouTube)
- [Metadata + thumbnails](#metadata--thumbnails--chapters)
- [Troubleshooting](#troubleshooting)
- [Files in this folder](#files-in-this-folder)
- [Adding support for a new site](#adding-support-for-a-new-site)

---

## Update yt-dlp

```powershell
yt-dlp -U
```

That's it. Updates to the latest in the current channel (nightly by default on this install — see `yt-dlp --version`). To switch channels: `yt-dlp --update-to nightly` or `--update-to stable`.

---

## Simple video download

```powershell
.\yt-dlp "URL"
```

Lands in the current directory. To put it elsewhere, use `-P`:

```powershell
.\yt-dlp -P "D:\Videos" "URL"
```

Also, the simple version above caps at 1080p.  To download at 4K (or highest available) use:
```
.\yt-dlp -S "res:2160" --merge-output-format mkv "URL"
```
That will produce an .mkv file.  If you need it to be mp4, then do the following:
```
.\yt-dlp -S "res:2160" --recode-video mp4 "URL"
```
The "recode-video" option will be slow.  But, may be the only option for producing .mp4.  The command below would be faster, but only works if the codecs already fit MP4. If they don't (e.g. VP9 + Opus from YouTube above 1080p) --remux-video mp4 errors out.
```
.\yt-dlp -S "res:2160" --remux-video mp4 "URL"
```

> **Firefox cookies note:** if Firefox is open and yt-dlp complains *"could not copy cookie database"* — close Firefox, then retry. If the default profile isn't picked up, override: `yt-dlp --cookies-from-browser firefox:"Path/to/profile" "URL"`. To skip cookies entirely for one run: `--no-cookies-from-browser`.

---

## Quality / resolution

> **⚠️ READ THIS BEFORE GRABBING 4K OR 1440p:** the config's `-t mp4` biases yt-dlp toward H.264 video, which on YouTube tops out at **1080p**. Anything above 1080p is VP9 or AV1 only. So a bare `yt-dlp` call against a 4K source silently caps at 1080p. Use one of the commands below to override.

### Common requests

| You want… | Command |
|---|---|
| **Absolute best — whatever's highest, no resolution cap** | `yt-dlp -f "bv*+ba/b" --merge-output-format mkv "URL"` |
| Target 4K (caps at 4K — picks 4K even if 8K is available) | `yt-dlp -S "res:2160" --merge-output-format mkv "URL"` |
| Target 1080p (caps at 1080p) | `yt-dlp -S "res:1080" "URL"` |
| Target 720p (caps at 720p) | `yt-dlp -S "res:720" "URL"` |
| Smallest filesize | `yt-dlp -S "+size,+br" "URL"` |
| Just see what formats exist | `yt-dlp -F "URL"` |

> **`-f` vs `-S` in one line:** `-f` is a hard format selector ("pick what matches this pattern"); `-S` is a soft sort key ("prefer closer to this"). On YouTube (which tops out at 4K), the first two rows produce identical results. They only diverge on 8K+ sources, where `-f "bv*+ba/b"` gets the 8K and `-S "res:2160"` caps at 4K (because 4K is the closest match to a target of 2160).

### Container choice when above 1080p

Above 1080p, YouTube serves VP9 or AV1 video. **MP4 doesn't accept VP9+Opus cleanly** — use MKV, or accept a slow re-encode:

- **MKV** (recommended, no re-encode): `--merge-output-format mkv`
- **MP4 with re-encode** (slow, lossy): `--recode-video mp4`

### Workflow — when in doubt, list first

```powershell
.\yt-dlp -F "URL"
```

That prints the format table. Look at the `RESOLUTION` column, pick the highest video-only row and the best audio-only row, then:

```powershell
.\yt-dlp -f "313+251" --merge-output-format mkv "URL"
```

(Example: format `313` = 4K VP9, `251` = best Opus audio. Substitute the actual IDs from your `-F` output.)

---

## Audio only

| You want… | Command |
|---|---|
| MP3 (default audio preset) | `yt-dlp -t mp3 "URL"` |
| FLAC (lossless) | `yt-dlp -x --audio-format flac "URL"` |
| WAV | `yt-dlp -x --audio-format wav "URL"` |
| Opus (smallest, modern) | `yt-dlp -x --audio-format opus "URL"` |
| AAC | `yt-dlp -t aac "URL"` |
| Best audio in original codec | `yt-dlp -f bestaudio "URL"` |

---

## Playlists

Standard playlist download (with skip-already-downloaded tracking):

```powershell
.\yt-dlp --download-archive downloaded.txt -o "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"
```

This:

- Creates a subfolder named after the playlist
- Numbers files by playlist position
- Writes each downloaded ID to `downloaded.txt` so subsequent runs skip them

### Slicing a playlist

| You want… | Add this flag |
|---|---|
| First 10 items | `-I :10` |
| Items 5 through 15 | `-I 5:15` |
| Last 5 | `-I -5:` |
| Reverse order | `-I ::-1` |
| Only this video, ignore the playlist it's in | `--no-playlist` |

### Filtering a playlist

| You want… | Add this |
|---|---|
| Only videos longer than 5 minutes | `--match-filters "duration>300"` |
| Only videos shorter than 1 hour | `--match-filters "duration<3600"` |
| Only HD-or-better | `--match-filters "height>=720"` |
| Uploaded after a date | `--match-filters "upload_date>20240101"` |

---

## Subtitles

| You want… | Command |
|---|---|
| English subs as a separate file | `yt-dlp --write-subs --sub-langs en "URL"` |
| English subs embedded in the video | `yt-dlp --embed-subs --sub-langs en "URL"` |
| All available subs | `yt-dlp --write-subs --sub-langs all "URL"` |
| Auto-generated (YouTube) | `yt-dlp --write-auto-subs --sub-langs en "URL"` |
| Convert subs to SRT format | add `--convert-subs srt` |

> **Foreign-language videos:** if the audio isn't English, add `--write-subs --sub-langs en` to grab English subtitles where available.

---

## Trim / clip / sections

| You want… | Command |
|---|---|
| Just 10:00 – 20:00 of a video | `yt-dlp --download-sections "*10:00-20:00" "URL"` |
| Frame-accurate cuts (slower, re-encodes) | add `--force-keyframes-at-cuts` |
| Just chapters matching a name | `yt-dlp --download-sections "CHAPTER_NAME" "URL"` |
| Multiple ranges | repeat the flag: `--download-sections "*0-30" --download-sections "*5:00-5:30"` |

---

## SponsorBlock (YouTube only)

| You want… | Command |
|---|---|
| Skip sponsor reads + self-promo | `yt-dlp --sponsorblock-remove sponsor,selfpromo "URL"` |
| Mark all segments as chapters (keep audio, just label) | `yt-dlp --sponsorblock-mark all "URL"` |
| Remove every common ad/filler segment | `yt-dlp --sponsorblock-remove default "URL"` |
| Remove everything except previews | `yt-dlp --sponsorblock-remove "all,-preview" "URL"` |

**Categories:** `sponsor`, `intro`, `outro`, `selfpromo`, `preview`, `filler`, `interaction`, `music_offtopic`, `hook`, `poi_highlight`, `chapter`. Prefix with `-` to exclude.

`default` is shorthand for "all except filler."

---

## Metadata + thumbnails + chapters

| You want… | Add this |
|---|---|
| Embed title/uploader/description in the video file | `--embed-metadata` |
| Embed thumbnail as cover art | `--embed-thumbnail` |
| Embed YouTube chapter markers | `--embed-chapters` |
| Save thumbnail as separate `.jpg` | `--write-thumbnail` |
| Save full metadata as `.info.json` | `--write-info-json` |
| **All of the above** | `--embed-metadata --embed-thumbnail --embed-chapters --write-info-json` |

---

## Troubleshooting

### Always try first

```powershell
.\yt-dlp -U
```

YouTube and other big sites change their APIs constantly. yt-dlp ships fixes within hours. Most "broken" reports are just an out-of-date binary.

### Common errors

| Error | Fix |
|---|---|
| **403 Forbidden** | Cookies are loaded by default. If still 403: `yt-dlp --update-to nightly`, then if needed `--extractor-args "youtube:player_client=default,android"` |
| **429 Too Many Requests** | Slow down: `yt-dlp -N 1 --sleep-requests 1 --min-sleep-interval 5 --max-sleep-interval 15 "URL"`. Permanent fix: comment out `-N 4` in `yt-dlp.conf`. |
| **Slow / low-bandwidth server** (download crawls but works) | Usually fine — let it run. For long downloads, add `--http-chunk-size 10M` so an interruption only loses the current chunk instead of restarting from the top. If speed *drops* during the download (CDN throttle ramp), also add `--throttled-rate 100K` to re-fetch the format URL when speed falls below 100 KB/s — sometimes returns a faster URL. |
| **Download stalls partway** (speed drops to ~0) | Some CDNs anti-leech by throttling after N seconds. `--throttled-rate 100K` re-fetches the URL when this happens. Combine with `--http-chunk-size 10M` for best resilience. |
| **"Video unavailable"** | Likely private/deleted/geo-blocked. For geo-blocks try `--xff default` or a VPN. |
| **"could not copy cookie database"** | Firefox is open with the cookie DB locked. Close Firefox, retry. |
| **"No formats found"** | Try `-f b` (best available, less strict). Check `-F` for what actually exists. |
| **Timeout / connection reset** | Built-in retries usually handle it; if persistent, add `--force-ipv4` |
| **Merge errors** | Make sure `ffmpeg.exe` is in this folder; force MP4 output: `--merge-output-format mp4` |
| **Age-restricted / member-only** | Cookies should cover this. Make sure you're logged into the platform in Firefox. |
| **"Unsupported URL"** | yt-dlp doesn't have an extractor for that site. Check `supportedsites.md` on the [yt-dlp repo](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md). |
| **`-N 4` cascading 429s on a non-YouTube site** | One-shot fix: prepend `-N 1` for that call. Permanent fix: edit `yt-dlp.conf` and comment out `-N 4`. |

---

## Files in this folder

| File | What it is |
|---|---|
| `yt-dlp.exe` | The downloader binary. Built from source in this same folder (the `yt_dlp/` subdir is the Python source). |
| `yt-dlp.exe.bak` | Previous version, kept after every build for one-rename rollback if a new build misbehaves. |
| `yt-dlp.conf` | Auto-loaded config. Edit to change defaults. |
| `ffmpeg.exe`, `ffprobe.exe`, `ffplay.exe` | Used for merging streams, post-processing, metadata reads. |
| `downloaded.txt` | Per-playlist archive of already-downloaded video IDs. Safe to delete to force re-download. |
| `yt-dlp-plugins\` | Drop third-party plugin packages here to extend yt-dlp without editing source. |
| `+Build yt-dlp+.bat` | Double-click to rebuild `yt-dlp.exe` from source. Handles backup, build, swap, and smoke test. |
| `+HOWTO+.md` | This file. |
| `+HOWTO+ (Add New Sites).md` | Step-by-step for writing your own extractor when yt-dlp doesn't support a site you need. |
| `yt_dlp\`, `bundle\`, `devscripts\`, `.venv\`, etc. | The yt-dlp source tree (a fork of `yt-dlp/yt-dlp`) and Python venv used to build it. |

---

## Adding support for a new site

If you hit *"Unsupported URL"* on a site you want to download from, see **`+HOWTO+ (Add New Sites).md`** in this same folder for the full workflow. It walks through creating a new extractor, running tests, and lint/format. Already-added custom extractors (not in the public yt-dlp release):

- **colliderporn.com** — aggregates videos from other hosts via iframe embeds
- **iceporn.com** — supports `/embed/<id>` and `/video/<id>/<slug>` patterns; handles `lq` (320p), `hq` (720p), and `4k` (2160p) variants

To rebuild `yt-dlp.exe` after adding/editing an extractor, double-click `+Build yt-dlp+.bat` in this folder (or ask Claude via the `/yt-dlp` command).

---

## Useful one-liners

```powershell
# Simulate / dry-run (no download, just show what would happen)
.\yt-dlp -s "URL"

# Dump complete metadata as JSON (handy for scripting)
.\yt-dlp -J "URL"

# Print just title + duration + date
.\yt-dlp --print title --print duration_string --print upload_date "URL"

# Test mode (downloads only 10 KiB — fast way to validate a URL works)
.\yt-dlp --test "URL"

# List subtitles available
.\yt-dlp --list-subs "URL"

# List thumbnails available
.\yt-dlp --list-thumbnails "URL"
```
