# Thí nghiệm cutoff của Mergesort — bản rà soát trước khi nộp

Sinh viên: **Nguyễn Lê Quang Minh — 25021877**. Báo cáo: [report/Bao_cao_cutoff_25021877_DRAFT.docx](report/Bao_cao_cutoff_25021877_DRAFT.docx).

Mục tiêu là khảo sát thời điểm chuyển từ mergesort sang insertion sort trên các đoạn nhỏ. `src/StudentMergeSort.java` là đúng bản mã đã chạy trong cả hai phiên, có SHA-256 `A207041F742F4629A1209D63BBA0DDD3ADDC49493D1E9A3E5A0C059F02F0DA5D`. Chú thích đầu tệp nói các thân hàm “để trống” là chú thích cũ từ khung bài tập; các hàm thực tế đã được điền. Giữ nguyên byte của tệp để đối chiếu với log đo.

## Kết quả có thể kiểm tra lại

- Hai phiên thực hiện trên Intel Core 5 120U, Windows, Java 25.0.2 vào 17/11/2026. Mỗi phiên gồm 24 bộ dữ liệu × 12 cutoff × 7 vòng = 2.016 thời gian.
- `CheckStudent` báo đúng thứ tự và ổn định trên 43.230 trường hợp ở từng phiên. Benchmark kiểm lại kết quả sau mỗi lần bấm giờ.
- Chỉ số chính: lấy trung vị 7 vòng cho từng bộ/cutoff, sau đó lấy trung bình nhân của `median(k=7) / median(k)` trên 24 bộ. Theo chỉ số này, k=7 đứng đầu cả hai phiên; k=10 thấp hơn 0,45% và 2,14%. Đây là lựa chọn thực dụng cho máy và bộ dữ liệu đã đo; sự dao động thời gian chưa cho phép khẳng định một ngưỡng tối ưu phổ quát.

Chi tiết và giới hạn ở báo cáo. Bản ghi gốc không bị làm sạch hoặc bỏ mẫu ngoại lệ.

## Cấu trúc

- `src/`: thuật toán, kiểm thử, sinh dữ liệu và benchmark.
- `data/`: 24 đầu vào đã dùng trong cả hai phiên.
- `results/run1/`, `results/run2/`: CSV gốc, log, môi trường, hash dữ liệu và bản sao mã nguồn tại thời điểm đo.
- `analysis/`: script kiểm toán hai phiên, bảng tổng hợp và biểu đồ. `generate_report.py` dựng lại DOCX từ các bảng.
- `scripts/`: chạy trên Windows và phân tích nhanh một CSV.
- `AI_USAGE.md`: phạm vi hỗ trợ AI.

## Chạy lại

Cần Java/JDK và Python 3. Trên PowerShell, tại thư mục gốc dự án:

```powershell
javac -d classes .\src\SortAlgorithm.java .\src\StudentMergeSort.java .\src\CheckStudent.java .\src\GenerateData.java .\src\Benchmark.java
java -cp classes CheckStudent
python .\analysis\analyze_runs.py
```

Lệnh Python kiểm tra số dòng, hash, mã nguồn, log và tạo lại `summary.csv`, `by_kind.csv`, `audit.txt`. Nếu có `matplotlib`, lệnh cũng dựng lại `cutoff_two_runs.png`. Để tạo lại báo cáo cần thêm `python-docx` rồi chạy `python .\analysis\generate_report.py`.

Để đo một phiên mới (có thể mất thời gian), chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_student.ps1 -Rounds 7
```

Script tự biên dịch, kiểm thử rồi ghi một thư mục mới trong `runs/`; nó không ghi đè kết quả hai phiên đã lưu. `data/` đã có sẵn; `GenerateData` chỉ dùng nếu cần tái tạo dữ liệu trong một thư mục khác.

**Trước khi nộp:** kiểm tra lại thông tin cá nhân trong báo cáo; đưa thư mục này lên một repository GitHub thuộc tài khoản sinh viên và nộp URL repository, không nộp URL của repository mẫu. Ảnh đề gốc ghi “log chat với AI (nếu có)”; theo thông tin sinh viên cung cấp, cô đã nói phần lịch sử chat không bắt buộc. Phần hỗ trợ AI vẫn được ghi rõ trong `AI_USAGE.md` và báo cáo.
