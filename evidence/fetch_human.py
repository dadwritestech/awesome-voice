"""Build the human baseline: prose written before ChatGPT (30 Nov 2022).

For each repo, take the README as it was at the last commit before 2022-06-01,
plus the bodies of releases published before that date. Uses the `gh` CLI.
Output: evidence/human.jsonl, one {"source", "kind", "text"} per line.
"""
import base64, json, subprocess, sys
from pathlib import Path

CUTOFF = "2022-06-01T00:00:00Z"
REPOS = """
psf/requests pallets/flask django/django tiangolo/fastapi encode/httpx python-poetry/poetry pypa/pipenv
expressjs/express vercel/next.js facebook/react vuejs/vue sveltejs/svelte webpack/webpack prettier/prettier
eslint/eslint jestjs/jest axios/axios lodash/lodash moment/moment date-fns/date-fns chalk/chalk yargs/yargs
sharkdp/bat sharkdp/fd BurntSushi/ripgrep junegunn/fzf ogham/exa jesseduffield/lazygit cli/cli
stedolan/jq tldr-pages/tldr ohmyzsh/ohmyzsh neovim/neovim tmux/tmux alacritty/alacritty
rust-lang/rustlings tokio-rs/tokio serde-rs/serde clap-rs/clap
spf13/cobra gin-gonic/gin gohugoio/hugo caddyserver/caddy traefik/traefik prometheus/prometheus
grafana/grafana hashicorp/terraform hashicorp/vault docker/compose kubernetes/minikube
rails/rails jekyll/jekyll Homebrew/brew discourse/discourse mastodon/mastodon
sqlite/sqlite redis/redis apache/superset metabase/metabase supabase/supabase
home-assistant/core syncthing/syncthing restic/restic borgbackup/borg rclone/rclone
obsproject/obs-studio mpv-player/mpv yt-dlp/yt-dlp ytdl-org/youtube-dl FFmpeg/FFmpeg
pandas-dev/pandas numpy/numpy scikit-learn/scikit-learn jupyter/notebook streamlit/streamlit
tailwindlabs/tailwindcss twbs/bootstrap d3/d3 chartjs/Chart.js mrdoob/three.js
microsoft/vscode atom/atom electron/electron tauri-apps/tauri denoland/deno oven-sh/bun
""".split()

def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None

out = Path(__file__).with_name("human.jsonl")
done = {json.loads(l)["source"] for l in out.open(encoding="utf-8")} if out.exists() else set()
with out.open("a", encoding="utf-8") as fh:
    for repo in REPOS:
        if repo in done:
            continue
        commits = gh(f"repos/{repo}/commits?until={CUTOFF}&per_page=1&path=README.md")
        rows = []
        if commits:
            sha = commits[0]["sha"]
            c = gh(f"repos/{repo}/contents/README.md?ref={sha}")
            if c and c.get("content"):
                rows.append({"source": repo, "kind": "readme", "date": commits[0]["commit"]["committer"]["date"],
                             "text": base64.b64decode(c["content"]).decode("utf-8", "replace")})
        rel = gh(f"repos/{repo}/releases?per_page=30") or []
        for r in rel:
            if r.get("published_at") and r["published_at"] < CUTOFF and (r.get("body") or "").strip():
                rows.append({"source": repo, "kind": "release", "date": r["published_at"], "text": r["body"]})
                if sum(x["kind"] == "release" for x in rows) >= 3:
                    break
        if not rows:
            rows = [{"source": repo, "kind": "none", "text": ""}]
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(repo, len(rows), file=sys.stderr)
