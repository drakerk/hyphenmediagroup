"""Pack the app source into one encrypted file for the (public) site repo, or unpack it.

    HYPHEN_SRC_KEY=<base64 key> python3 -I tools/pack.py pack   <tb dir> <repo>/source/hyphen-src.tar.gz.enc
    HYPHEN_SRC_KEY=<base64 key> python3 -I tools/pack.py unpack <repo>/source/hyphen-src.tar.gz.enc <tb dir>

Left out of the bundle: screenshots, the built out/ folder, site/api.json (its url/token are passed in
separately), and src/files, src/photos, src/media: the site publishes those, so unpack copies them back
from the repo (plain unreleased audio is never in the repo; build_site.py carries the encrypted copies over).
The bundle is deterministic: unchanged source gives identical bytes, so git stores nothing new. The key lives only in the daily scheduled task, never in the repo."""
import base64, io, os, sys, tarfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SKIP_DIRS = {"out", "__pycache__", ".git"}
def skip(rel):
    parts = rel.split(os.sep)
    if parts[0] in SKIP_DIRS: return True
    # published as-is by the site, so unpack restores them from the repo instead of storing them twice
    if parts[:2] in (["src", "files"], ["src", "photos"], ["src", "media"]): return True
    if rel == os.path.join("site", "api.json"): return True
    if len(parts) == 1 and (rel.endswith(".png") or rel.startswith("shot")): return True
    if rel.endswith(".bak") or (parts[0] == "ref" and rel.endswith(".html")): return True
    return False

key = base64.b64decode(os.environ["HYPHEN_SRC_KEY"])
mode, a, b = sys.argv[1:4]
if mode == "pack":
    import gzip, hashlib, hmac
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for root, dirs, files in os.walk(a):
            dirs[:] = sorted(d for d in dirs if not skip(os.path.relpath(os.path.join(root, d), a)))
            for f in sorted(files):
                rel = os.path.relpath(os.path.join(root, f), a)
                if not skip(rel):
                    ti = tar.gettarinfo(os.path.join(root, f), rel); ti.mtime = 0; ti.uid = ti.gid = 0; ti.uname = ti.gname = ""
                    tar.addfile(ti, open(os.path.join(root, f), "rb"))
    data = gzip.compress(buf.getvalue(), mtime=0)
    iv = hmac.new(key, hashlib.sha256(data).digest(), "sha256").digest()[:12]
    os.makedirs(os.path.dirname(b), exist_ok=True)
    open(b, "wb").write(iv + AESGCM(key).encrypt(iv, data, None))
    print("packed", len(data) // 1024, "KB ->", b)
elif mode == "unpack":
    raw = open(a, "rb").read()
    data = AESGCM(key).decrypt(raw[:12], raw[12:], None)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        tar.extractall(b, filter="data")
    import shutil
    repo = os.path.dirname(os.path.dirname(os.path.abspath(a)))
    for src, dst in (("files", "src/files"), ("photos", "src/photos"), ("media/img", "src/media/img"), ("media/docs", "src/media/docs")):
        if os.path.isdir(os.path.join(repo, src)):
            shutil.copytree(os.path.join(repo, src), os.path.join(b, dst), dirs_exist_ok=True)
    os.makedirs(os.path.join(b, "src/media/audio"), exist_ok=True)
    print("unpacked into", b, "(files, photos and media images restored from the site)")
