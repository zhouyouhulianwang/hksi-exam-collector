"""
HKSI LE Exam Question Bank Collector
Collects all questions from 51exampass.com
Key: different `identification` param returns different random 10-question samples
"""

import json, random, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import login, get_mgr_headers, PAPERS, BASE_URL
import requests


def fetch_questions(ident, ch_id, item_id, token):
    headers = get_mgr_headers(token)
    params = {"small_id": ch_id, "type": "sele", "order_item_id": item_id,
              "identification": ident, "page": 1, "limit": 200}
    try:
        resp = requests.post(f"{BASE_URL}/v1.question/getQuestionPaper",
                            headers=headers, data=params, timeout=15)
        data = resp.json()
        if data.get("code") == 1:
            return data.get("data", {}).get("data", [])
    except:
        pass
    return []


def collect_chapter(ch_id, item_id, expected, token, max_rounds=300):
    all_q = {}
    rounds, no_new = 0, 0
    while rounds < max_rounds and no_new < 30:
        rounds += 1
        idents = [f"c_{i}_{random.randint(10000,999999)}" for i in range(20)]
        with ThreadPoolExecutor(max_workers=20) as ex:
            futures = {ex.submit(fetch_questions, ident, ch_id, item_id, token): ident for ident in idents}
            new = 0
            for f in as_completed(futures):
                for q in f.result():
                    qid = q["id"]
                    if qid not in all_q:
                        new += 1
                        all_q[qid] = {"id": q["id"], "questionType": int(q.get("question_type",1)),
                                       "content": q.get("content",""), "options": q.get("options",[]),
                                       "answer": q.get("answer",""), "analysis": q.get("analysis",""),
                                       "score": q.get("score",0), "knowledgePoints": q.get("knowledge_points","")}
        if new == 0: no_new += 1
        else: no_new = 0
        if len(all_q) >= expected: break
    return list(all_q.values())


def collect_all(username, password, output_dir="../data"):
    print("="*60)
    print("HKSI LE Question Bank Collector")
    print("="*60)
    token = login(username, password)
    print("Login OK\n")
    os.makedirs(output_dir, exist_ok=True)
    all_papers = []
    for name, cfg in PAPERS.items():
        print(f"\n=== {name} (item_id={cfg['item_id']}) ===")
        paper = {"paperName": name, "subjectId": cfg["subject_id"],
                 "orderItemId": cfg["item_id"], "chapters": []}
        for ch in cfg["chapters"]:
            qs = collect_chapter(ch["id"], cfg["item_id"], 0, token)
            paper["chapters"].append({"chapterId": ch["id"], "chapterName": ch["name"],
                                       "expectedCount": len(qs), "actualCount": len(qs), "questions": qs})
            print(f"  {ch['name']}: {len(qs)} questions")
        total = sum(len(c["questions"]) for c in paper["chapters"])
        path = os.path.join(output_dir, f"{name}_完整题库.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(paper, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {total} questions -> {path}")
        all_papers.append(paper)
    with open(os.path.join(output_dir, "全部题库.json"), "w", encoding="utf-8") as f:
        json.dump(all_papers, f, ensure_ascii=False, indent=2)
    grand = sum(len(c["questions"]) for p in all_papers for c in p["chapters"])
    print(f"\n{'='*60}\nTotal: {grand} questions\nOutput: {output_dir}")
    return all_papers


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python collect_questions.py <username> <password> [output_dir]")
        sys.exit(1)
    collect_all(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "../data")
