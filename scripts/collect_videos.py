"""
HKSI LE Video Downloader
"""
import json, os, subprocess


def download_all(manifest_path="../materials/video_manifest.json", output_dir="../materials/videos"):
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    os.makedirs(output_dir, exist_ok=True)
    all_v = []
    for p, vs in manifest.items():
        for v in vs: all_v.append((p, v))
    ok = fail = total = 0
    for i, (p, v) in enumerate(all_v, 1):
        url = v["videoUrl"]
        sn = v["name"].replace("/","_").replace("\\","_").replace(":","_").replace(" ","_") or f"{p}_video_{v['id']}"
        fn = f"{sn}.mp4"
        fp = os.path.join(output_dir, fn)
        if os.path.exists(fp) and os.path.getsize(fp) > 10*1024*1024:
            total += os.path.getsize(fp)
            print(f"[{i}] {fn}: {os.path.getsize(fp)/1024/1024:.1f}MB (exists)")
            ok += 1; continue
        print(f"[{i}/{len(all_v)}] {fn}...", end=" ", flush=True)
        try:
            subprocess.run(["curl","-L","-o",fp,"-s","--max-time","300","--retry","2",
                           "-H","User-Agent: Mozilla/5.0",url], timeout=330, capture_output=True)
            if os.path.exists(fp) and os.path.getsize(fp) > 10*1024*1024:
                total += os.path.getsize(fp)
                print(f"OK ({os.path.getsize(fp)/1024/1024:.1f}MB)")
                ok += 1
            else:
                print("FAIL")
                if os.path.exists(fp): os.remove(fp)
                fail += 1
        except Exception as e:
            print(f"ERR: {e}"); fail += 1
    print(f"\nDone: {ok} OK, {fail} failed, {total/1024/1024:.1f}MB total")


if __name__ == "__main__":
    import sys
    mp = sys.argv[1] if len(sys.argv) > 1 else "../materials/video_manifest.json"
    od = sys.argv[2] if len(sys.argv) > 2 else "../materials/videos"
    download_all(mp, od)
