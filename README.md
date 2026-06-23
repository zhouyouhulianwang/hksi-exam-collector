# HKSI LE Exam Data Collector

Collects question banks, videos, courseware, and exam papers for HKSI LE (Hong Kong Securities and Investment Institute Licensing Examination) Papers 1, 2, and 6 from 51exampass.com.

## Collected Data

| Paper | Chapters | Questions | Videos | Courseware |
|-------|----------|-----------|--------|------------|
| Paper 1 (Paper 1) | 9 | 1,444 | 9 | 1 PDF |
| Paper 2 (Paper 2) | 7 | 636 | 11 | 1 PDF |
| Paper 6 (Paper 6) | 4 | 1,206 | 5 | 2 PDFs |
| **Total** | **20** | **3,286** | **25** | **4 PDFs** |

- 11 preset exam papers + 2 auto-generated exam papers
- 6 HKSI official sample papers (PDF)
- Video/chapter/courseware mapping table

## Project Structure

```
.
├── scripts/
│   ├── collect_questions.py      # Question bank collector
│   ├── collect_materials.py      # Materials collector (videos, courseware, papers)
│   ├── collect_videos.py         # Video downloader
│   └── utils.py                  # API utilities
├── data/                         # Collected question banks
│   ├── Paper 1_完整题库.json
│   ├── Paper 2_完整题库.json
│   ├── Paper 6_完整题库.json
│   ├── 全部题库.json
│   ├── 资料对应表.json
│   ├── 资料对应表.md
│   ├── Paper 1/预设模拟卷/
│   ├── Paper 2/预设模拟卷/
│   └── Paper 6/预设模拟卷/
└── materials/                    # Courseware PDFs and video manifests
    ├── video_manifest.json
    ├── *_courseware.pdf
    ├── *_样题.pdf
    └── videos/                   # Downloaded videos (run collect_videos.py)
```

## Requirements

- Python 3.8+
- `requests`
- `curl` (for video downloads)
- Valid 51exampass.com account

```bash
pip install -r requirements.txt
```

## Usage

### 1. Collect Question Banks

```bash
cd scripts
python collect_questions.py <username> <password> [output_dir]
```

### 2. Collect Materials (Video URLs, Courseware, Exam Papers)

```bash
python collect_materials.py <username> <password>
```

### 3. Download Videos

```bash
python collect_videos.py [manifest_path] [output_dir]
```

## How It Works

The `getQuestionPaper` API returns 10 random questions per call. Different `identification` parameter values return different random samples. By making hundreds of parallel requests with different identifications, all unique questions are collected.

```python
def fetch(ident, chapter_id, item_id, token):
    params = {
        'small_id': chapter_id,
        'type': 'sele',
        'order_item_id': item_id,
        'identification': ident,  # Different = different sample
        'page': 1, 'limit': 200
    }
    # Returns 10 random questions
```

## Disclaimer

For educational and personal study purposes only. Respect 51exampass.com's terms of service.

## License

MIT
