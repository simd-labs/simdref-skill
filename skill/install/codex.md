## Codex install and updates

Preferred (marketplace one-liner, from a Codex CLI prompt):

```
codex plugin marketplace add simd-labs/simdref-skill
/plugins
```

Pick `asm-analysis` and enable it.

Manual install — Codex discovers skills from `.agents/skills/` (repo)
or `~/.agents/skills/` (user). See the
[Codex skills docs](https://developers.openai.com/codex/skills).

```bash
git clone https://github.com/simd-labs/simdref-skill.git ~/src/simdref-skill
mkdir -p ~/.agents/skills
ln -sf ~/src/simdref-skill/codex-skills/asm-analysis/skills/asm-analysis \
       ~/.agents/skills/asm-analysis
```

Refresh by updating the checkout: `(cd ~/src/simdref-skill && git pull)`.
