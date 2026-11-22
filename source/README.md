# Hyphen app: source and daily refresh

The app's source lives in `source/hyphen-src.tar.gz.enc` (AES-GCM, encrypted). The key is kept only in
the daily scheduled task. This file is the only plain part of the source in this repo.

## Unpack

    HYPHEN_SRC_KEY=<key> python3 -I tools/pack.py unpack <repo>/source/hyphen-src.tar.gz.enc <work dir>

(`source/pack.py` is a plain copy of the same tool, so a fresh run can unpack with it.)
Photos, PDFs and media images come back from the published site. Plain demo audio is never stored here.

## Where each part of the data lives (edit these, never the built files)

| Part | File | How it updates |
| --- | --- | --- |
| Macy's dates, day sheets, people | `ref/macy_data.json` | `tools/pull_macy.py` from her own tour book |
| Stephen's dates, day sheets, people | `ref/ss_data.json` | edit from his calendar / tracker / advances |
| colby!'s dates | `merge.py` (colby! section) | edit from her calendar / CAA mail |
| Deals (management) | `merge.py` (FEE / RUN / colby deal) and `ref/ss_deals.json` | edit from offers and memos |
| Key dates | `ref/keydates.json` | edit (artist, date, kind, title, sub) |
| Writes | `raw/cal_macy.json`, `raw/cal_stephen.json`, `COLBY_WRITES` in `writes.py` | re-pull calendars, run `writes.py` |
| Demos / masters | `ref/mgmt.json` → `music` | add a track entry; new audio goes in `src/media/audio/` |
| Hero slideshow | `HERO` in `src/app.js`, photos in `src/photos/hero/` | edit |

`mgmt.py` and `keydates.py` were the first imports and are not re-run.

## Build and publish

    tools/refresh.sh <work dir> <repo clone> <app password> <api.json>

Then commit and push the repo, and patch the claude.ai version with `out/index.html` plus any new files.

## Rules

- Never commit the app password, the api token or the source key.
- Unreleased audio is only ever published encrypted.
- No fees or deal terms outside the deals section.
