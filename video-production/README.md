# Bộ skill sản xuất video cho Codex

Snapshot: **2026-11-17**. Bao gồm **19 skill**: 9 tên mới, 4 core HyperFrames cập nhật và 6 entrypoints tương thích. Các framework/app, credentials và dữ liệu video cá nhân không được đóng gói.

## Cài lại an toàn

Yêu cầu Python 3.10+. Clone repo, kiểm tra package rồi chạy installer:

```powershell
git clone https://github.com/Chau165/local_skill.git
Set-Location local_skill
python video-production/install.py --verify-only
python video-production/install.py --dry-run
python video-production/install.py
```

Installer dùng `%USERPROFILE%/.agents/skills` (hoặc `~/.agents/skills` trên macOS/Linux). Trước khi thay một skill khác nội dung, nó chuyển nguyên thư mục cũ vào backup trong `<CODEX_HOME>/backups/video-production/<timestamp>/`. Chỉ 19 tên trong manifest được quản lý; global AGENTS.md, config.toml, các skill khác, credentials và PATH không bị thay đổi. Các SKILL.md trùng tên dưới `<CODEX_HOME>/skills` được archive để tránh hai bộ active; support-only references được giữ cho workflow faceless cũ, không tạo skill trùng.

Preset legacy gốc được cài ngoài vùng skill discovery tại `<CODEX_HOME>/video-presets/video-production-20261117/`. Chỉ dùng khi chủ động chọn illustrated/cartoon/world-motion; không cài trực tiếp các SKILL.md bên trong presets thành một bộ global thứ hai.

Muốn tạo workspace video riêng trong cùng lần cài:

```powershell
python video-production/install.py --workspace "$env:USERPROFILE\Documents\AI-Video-Production"
```

Workspace phải mới hoặc trống; installer từ chối ghi đè AGENTS.md đã có. Không chép workspace/AGENTS.md vào global Codex hoặc project backend. Có thể đặt `--skills-root` và `--codex-home` để cài vào vị trí khác. Sau cài hãy mở chat Codex mới. Không chạy restore-codex.ps1 cũ sau add-on này vì snapshot cũ có thể ghi đè skill mới; nếu cần restore toàn bộ cấu hình cũ, chạy add-on video sau cùng.

## Rollback

Installer in đường dẫn receipt.json sau khi cài. Dùng đúng receipt đó:

```powershell
python video-production/install.py --rollback "DUONG_DAN_BACKUP\receipt.json" --dry-run
python video-production/install.py --rollback "DUONG_DAN_BACKUP\receipt.json"
```

Rollback kiểm tra hash backup trước khi đổi file, giữ bản hiện tại trong quarantine rồi khôi phục bản cũ. Không xóa đệ quy. Nếu gặp lỗi cài một phần, giữ receipt/backup để khôi phục; không xóa chúng. Việc clone repo chỉ là backup, chưa tự động thay cài đặt máy.

## Danh sách skill

| Skill | Công dụng |
|---|---|
| `hyperframes` | Entry point and deterministic HTML video contract |
| `hyperframes-cli` | Scaffold, validate, snapshot, preview and render |
| `hyperframes-registry` | Find and install editable blocks/components |
| `media-use` | Source, prepare and track media assets |
| `reverse-any-video` | Reference-video reconstruction; provider/Pro access may be required |
| `style-sampling` | Selected style/episode sampling; provider/Pro access may be required |
| `hyperframes-core` | Neutral compatibility entrypoint for composition/timing |
| `hyperframes-animation` | Neutral compatibility entrypoint for finite animation |
| `hyperframes-creative` | Neutral compatibility entrypoint for story/design |
| `hyperframes-keyframes` | Neutral compatibility entrypoint for seek-safe keyframes |
| `lottie-motion` | Use Lottie/dotLottie assets when selected |
| `svg-paperjs` | SVG/Paper.js support graphics, charts and paths |
| `remotion-best-practices` | Router covering Remotion project/composition practices |
| `remotion-captions` | Caption/subtitle guidance for Remotion |
| `remotion-docs` | Look up current Remotion documentation |
| `reference-design-contract` | Translate references into an evidence-based design contract |
| `motion-design` | Motion craft, continuity, pacing and typography |
| `gsap-timeline` | Sequence and coordinate GSAP timeline animations |
| `video-production-workflow` | Source-faithful editing, original voice, full captions, timestamped graphics and fact checks |

## Phạm vi và phiên bản

- HyperFrames CLI pin **0.9.59** trong launcher; source skill commit và patch được ghi trong manifest. Có local source-fidelity/style/update patches nên skills check có thể báo khác hash upstream; không tự updater ghi đè để làm check xanh.
- Remotion skills **4.0.544**; không đóng gói React/Remotion runtime. Chỉ cài framework vào một video project cần nó.
- OpenDesign chỉ gồm 3 helper tự dùng được; không cần cài app, daemon hoặc MCP. gsap-timeline được OpenDesign tuyển chọn từ GreenSock.
- Phụ thuộc render/STT được cài theo máy: Node >=22, browser, FFmpeg/FFprobe, và Whisper.cpp/model nếu cần xử lý giọng nói cục bộ. Không có executable hay model lớn trong repo này.
- Tôn trọng nguồn gốc, original voice và caption toàn bộ phần có lời. Minh họa theo quote/timestamp. Không tự sửa số liệu hoặc lời thuyết trình; thông tin thời gian thực cần nguồn/as-of và xác nhận trước khi sửa.

Nguồn và giấy phép: manifest.json, NOTICE.md, licenses/ và các notice gốc trong từng skill. Line endings được chuẩn hóa LF; Các path cá nhân của máy nguồn đã được thay bằng placeholder; wrapper world-motion-audit trỏ về máy Surface cũ được thay bằng implementation đầy đủ có sẵn; không chứa cấu hình tài khoản.

## Kiểm thử

Chạy `python video-production/install.py --verify-only` để kiểm checksum. Kịch bản kiểm thử installer nằm ở tests/test_install.py. Snapshot nguồn đã được Codex phát hiện đủ 19 skill và chạy thành công một smoke render neutral 6 giây có caption tiếng Việt và biểu đồ giả định. Kết quả đó không thay thế việc kiểm dependencies/render và speech accuracy trên máy mới.
