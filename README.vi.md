# CodexAgentRules - Linux Edition (AI Translated)

Đây là bộ quy tắc và công cụ hỗ trợ cho Codex agent trên Linux.

Repo này lưu lại cách làm việc anh đã thiết kế: trao đổi ngắn gọn bằng tiếng Việt, đọc hiểu dự án qua `project graph` trước khi sửa code, làm việc trên branch rõ ràng, commit có kỷ luật, và dùng agent chính để điều phối/review các việc được giao cho sub-agent.

## Thuật ngữ

- `agent`: tác nhân AI thực hiện việc đọc, sửa, kiểm tra code.
- `project graph`: đồ thị mô tả cấu trúc dự án, gồm file, module, class, function, feature, test và quan hệ giữa chúng.
- `workflow`: quy trình làm việc.
- `feature branch`: nhánh Git riêng cho một tính năng hoặc thay đổi.
- `sub-agent`: agent phụ, được giao các việc nhỏ hơn.
- `graph tooling`: các script và file hỗ trợ tạo/truy vấn project graph.

## Nội dung dự án

### `rules/`

Các quy tắc chính cho agent:

- **[01-core-agent-rules.md](rules/01-core-agent-rules.md)**: định danh, cách giao tiếp, workflow, định dạng phản hồi cuối.
- **[02-coding-rules.md](rules/02-coding-rules.md)**: phong cách code, quy ước Python, hiệu năng và quy tắc IO.
- **[03-project-graph-rules.md](rules/03-project-graph-rules.md)**: schema SQLite cho project graph, loại node/edge, yêu cầu cập nhật graph.
- **[INDEX.md](rules/INDEX.md)**: bảng tra nhanh để biết nên đọc rule nào.

### `example_project_rule/`

- **[AGENTS.md](example_project_rule/AGENTS.md)**: mẫu quy tắc cấp dự án, dùng để copy vào các repo ứng dụng.

### `scripts/`

- **setup_project_rules.py**: cài `AGENTS.md`, graph scripts, graph schema và các mục `.gitignore` vào dự án đích.
- **update_project_graph.py**: quét dự án đích và tạo/cập nhật `project_graph.sqlite`.
- **query_project_graph.py**: tìm node trong graph và xem quan hệ giữa các node.

### `docs/`

- **graph-schema.md**: tài liệu schema của project graph, dạng dễ đọc cho người và agent.

## Quy tắc workflow chính

Sau khi setup vào một dự án, agent cần làm theo các quy tắc này:

- Đọc rule liên quan trước khi sửa code.
- Lập kế hoạch ngắn trước khi thay đổi code hoặc file.
- Truy vấn project graph trước khi làm feature; nếu đã có dữ liệu graph thì không dựa vào trí nhớ.
- Tạo feature branch trước khi làm tính năng.
- Commit sau mỗi feature, bugfix, refactor, thay đổi hành vi, thay đổi function/class hoặc cập nhật test đã hoàn tất.
- Chạy test/check phù hợp trước khi báo xong.
- Cập nhật project graph sau mỗi thay đổi code, test hoặc hành vi.
- Sau khi test pass trên feature branch, chờ anh duyệt trước khi merge.
- Giữ graph tooling chỉ ở local trong dự án đích; không commit graph scripts hoặc database artifacts vào repo ứng dụng trừ khi anh yêu cầu rõ.

## Mô hình agent chính và phân việc

Agent chính đóng vai trò như senior technical lead của anh:

- Chia việc lớn thành các task nhỏ.
- Dùng project graph làm ngữ cảnh trước khi giao việc hoặc sửa code.
- Giao các việc phụ phù hợp cho sub-agent khi có.
- Chịu trách nhiệm chất lượng cuối: review phần được giao, tích hợp thay đổi, chạy test, cập nhật graph và commit.
- Không dùng sub-agent để thay thế review. Agent chính vẫn chịu trách nhiệm cuối cùng.

## Quy tắc về constants

- Nếu một giá trị được dùng lặp lại nhiều nơi, ưu tiên đưa vào constant thay vì hardcode nhiều lần.
- Nếu constant dùng chung cho cả `core` và `ui`, đặt nó trong `shared`.

## Cài vào một dự án

Chạy từ repo này:

```bash
python3 scripts/setup_project_rules.py /path/to/project \
  --project-id project:your_project \
  --local-roots core,ui,shared,models,tests,main
```

Ví dụ cho dự án kiểu WaydroidMgr:

```bash
python3 scripts/setup_project_rules.py /home/foxnq/Projects/WaydroidMgr \
  --project-id project:waydroidmgr \
  --local-roots core,models,shared,ui,tests,main
```

Script setup sẽ cài hoặc cập nhật:

- `AGENTS.md`
- `docs/graph-schema.md`
- `scripts/update_project_graph.py`
- `scripts/query_project_graph.py`
- các mục `.gitignore` cho artifact của project graph

Mặc định, file đã tồn tại sẽ được giữ nguyên. Dùng `--force` nếu muốn ghi đè các file agent/graph hiện có:

```bash
python3 scripts/setup_project_rules.py /path/to/project --force
```

## File sinh ra trong dự án đích

Dự án đích thường nên ignore các artifact cục bộ này:

```text
project_graph.sqlite
project_graph.sqlite-*
docs/graph-schema.md
scripts/update_project_graph.py
scripts/query_project_graph.py
```

`AGENTS.md` thường nên được commit, vì nó ghi lại workflow của dự án cho các phiên agent sau.

## Tạo và truy vấn project graph

Sau khi setup, chạy trong dự án đích:

```bash
python3 scripts/update_project_graph.py
python3 scripts/query_project_graph.py "feature OR MainWindow" --limit 20
python3 scripts/query_project_graph.py "feature:event_bus" --edges
```

Dùng graph query trước khi làm feature để hiểu file, function, test, dependency và các quyết định liên quan đã có trong dự án.

Sau khi thay đổi code hoặc test, cập nhật graph để ngữ cảnh của dự án luôn mới.

## Schema của graph database

### Bảng `nodes`

| Cột | Kiểu | Mục đích |
| --- | --- | --- |
| `id` | TEXT (PK) | ID ổn định, ví dụ `file:path`, `class:module.Name`, `function:module.name`. |
| `type` | TEXT | Loại thực thể: `project`, `module`, `file`, `class`, `function`, `feature`, `test`, v.v. |
| `name` | TEXT | Tên dễ đọc. |
| `path` | TEXT | Đường dẫn file, tính từ thư mục gốc dự án. |
| `summary` | TEXT | Docstring hoặc mô tả ngắn. |
| `updated_at` | TEXT | Thời điểm cập nhật theo UTC. |
| `meta` | JSON | Metadata bổ sung, ví dụ module, số dòng, cờ async, thông tin lỗi cú pháp. |

### Bảng `edges`

| Cột | Kiểu | Mục đích |
| --- | --- | --- |
| `src` | TEXT | ID node nguồn. |
| `rel` | TEXT | Loại quan hệ. |
| `dst` | TEXT | ID node đích. |
| `meta` | JSON | Metadata bổ sung cho quan hệ, nếu có. |

### Loại node

```text
project module file function class feature bugfix refactor test decision todo dependency
```

### Loại quan hệ

```text
contains touches adds modifies implements depends_on calls tested_by fixes refactors documents supersedes related_to
```

## Cấu trúc file

```text
CodexAgentRules/
├── docs/
│   └── graph-schema.md
├── example_project_rule/
│   └── AGENTS.md
├── rules/
│   ├── 01-core-agent-rules.md
│   ├── 02-coding-rules.md
│   ├── 03-project-graph-rules.md
│   └── INDEX.md
├── scripts/
│   ├── query_project_graph.py
│   ├── setup_project_rules.py
│   └── update_project_graph.py
├── requirements.txt
└── README.md
```

## Phát triển repo này

- Sửa rule trong `rules/`.
- Sửa mặc định cấp dự án trong `example_project_rule/AGENTS.md`.
- Sửa hành vi installer trong `scripts/setup_project_rules.py`.
- Tạo lại graph cho dự án đích bằng `python3 scripts/update_project_graph.py` trong chính dự án đó.

## License

Giống Codex Linux project.
