# Agent entrypoint

Canonical bootstrap: `AGENTS.md` -> `memory/manifest.json` -> `python3 tools/context.py bootstrap`.

Do not start with the workbook or recursively read `wiki/`; they are secondary projections.

```bash
python3 tools/context.py entity coreweave
python3 tools/context.py topic token_economics
python3 tools/context.py open
python3 tools/validate.py
```
