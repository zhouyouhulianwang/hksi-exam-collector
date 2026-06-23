"""
HKSI LE Materials Collector - videos, courseware, exam papers
"""

import json, os, requests
from utils import login, get_mgr_headers, PAPERS, BASE_URL


def collect_video_urls(token):
    manifest = {}
    for name, cfg in PAPERS.items():
        manifest[name] = []
        r = requests.post(f"{BASE_URL}/v1.index/subject_detail",
                         headers=get_mgr_headers(token),
                         data={"id": cfg["subject_id"], "order_item_id": cfg["item_id"]}).json()
        if r.get("code") == 1:
            for ch in r["data"].get("small_list", []):
                for cls in ch.get("class", []):
                    if cls.get("video_url"):
                        manifest[name].append({"id": cls["id"], "name": cls.get("name",""),
                                               "chapterId": ch["id"], "videoUrl": cls["video_url"]})
    return manifest


def collect_courseware(token):
    cw = {}
    for name, cfg in PAPERS.items():
        cw[name] = []
        r = requests.post(f"{BASE_URL}/v1.index/subject_detail",
                         headers=get_mgr_headers(token),
                         data={"id": cfg["subject_id"], "order_item_id": cfg["item_id"]}).json()
        if r.get("code") == 1:
            for ch in r["data"].get("small_list", []):
                for cls in ch.get("class", []):
                    c = cls.get("courseware", {})
                    if c and c.get("url"):
                        cw[name].append({"chapterId": ch["id"], "lessonId": cls["id"],
                                         "lessonName": cls.get("name",""),
                                         "coursewareName": c.get("name",""), "coursewareUrl": c["url"]})
    return cw


def collect_exam_papers(token, output_dir="../data"):
    for name, cfg in PAPERS.items():
        r = requests.post(f"{BASE_URL}/v1.index/subject_detail",
                         headers=get_mgr_headers(token),
                         data={"id": cfg["subject_id"], "order_item_id": cfg["item_id"]}).json()
        if r.get("code") != 1: continue
        d = r["data"]
        for key, dirname in [("mock_exam", "预设模拟卷"), ("auto_mock_exam", "自动生成模拟卷")]:
            exams = d.get(key, [])
            if exams:
                pdir = os.path.join(output_dir, name, dirname)
                os.makedirs(pdir, exist_ok=True)
                for i, e in enumerate(exams, 1):
                    with open(os.path.join(pdir, f"{dirname} - 试卷{i}.json"), "w", encoding="utf-8") as f:
                        json.dump(e, f, ensure_ascii=False, indent=2)
                    qc = len(e.get("questions",[])) if isinstance(e, dict) else 0
                    print(f"  {name} {dirname} {i}: {qc} questions")


def download_courseware(courseware, output_dir="../materials"):
    os.makedirs(output_dir, exist_ok=True)
    seen = set()
    for paper, items in courseware.items():
        for it in items:
            url = it["coursewareUrl"]
            if url in seen: continue
            seen.add(url)
            fname = f"{paper}_courseware.pdf"
            path = os.path.join(output_dir, fname)
            if os.path.exists(path): continue
            try:
                r = requests.get(url, timeout=60)
                if r.status_code == 200:
                    with open(path, "wb") as f: f.write(r.content)
                    print(f"  OK {fname} ({len(r.content)/1024/1024:.1f}MB)")
            except Exception as e:
                print(f"  ERR {fname}: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python collect_materials.py <username> <password>")
        sys.exit(1)
    token = login(sys.argv[1], sys.argv[2])
    print("Login OK\n")

    print("=== Collecting video URLs ===")
    v = collect_video_urls(token)
    for p, vs in v.items(): print(f"  {p}: {len(vs)} videos")
    with open("../materials/video_manifest.json", "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)

    print("\n=== Collecting courseware ===")
    cw = collect_courseware(token)
    for p, cs in cw.items(): print(f"  {p}: {len(cs)} items")

    print("\n=== Collecting exam papers ===")
    collect_exam_papers(token)

    print("\n=== Downloading courseware PDFs ===")
    download_courseware(cw)

    print("\nDone! Run collect_videos.py to download video files.")
