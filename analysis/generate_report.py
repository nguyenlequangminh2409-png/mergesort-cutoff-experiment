"""Build the Vietnamese draft report after analyze_runs.py has audited the CSVs."""

import csv
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
summary = list(csv.DictReader((ROOT / "analysis" / "summary.csv").open(encoding="utf-8")))
by_kind = list(csv.DictReader((ROOT / "analysis" / "by_kind.csv").open(encoding="utf-8")))
doc = Document()
section = doc.sections[0]
section.page_height, section.page_width = Cm(29.7), Cm(21)
section.top_margin = section.bottom_margin = Cm(2.1)
section.left_margin = section.right_margin = Cm(2.25)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.15
for name, size in (("Title", 14), ("Heading 1", 12)):
    style = doc.styles[name]
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_before = Pt(9)
    style.paragraph_format.space_after = Pt(5)


def paragraph(text="", bold_label=None):
    p = doc.add_paragraph()
    if bold_label:
        p.add_run(bold_label).bold = True
    p.add_run(text)
    return p


def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, header in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = str(header)
        if widths:
            cell.width = Cm(widths[i])
    for values in rows:
        cells = t.add_row().cells
        for i, value in enumerate(values):
            cells[i].text = str(value)
            if widths:
                cells[i].width = Cm(widths[i])
    for row_number, row in enumerate(t.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cell.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(9)
                    if row_number == 0:
                        run.bold = True
    for row_index in (0, len(t.rows) - 1):
        for cell in t.rows[row_index].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            borders = tcPr.first_child_found_in("w:tcBorders")
            if borders is None:
                borders = OxmlElement("w:tcBorders")
                tcPr.append(borders)
            side = "top" if row_index == 0 else "bottom"
            edge = OxmlElement("w:" + side)
            edge.set(qn("w:val"), "single")
            edge.set(qn("w:sz"), "6")
            borders.append(edge)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


p = doc.add_paragraph()
p.add_run("HỌ VÀ TÊN: ").bold = True
p.add_run("Nguyễn Lê Quang Minh")
p = doc.add_paragraph()
p.add_run("MÃ SINH VIÊN: ").bold = True
p.add_run("25021877")
p = doc.add_paragraph()
p.add_run("MÔN HỌC: ").bold = True
p.add_run("Cấu trúc dữ liệu và Giải thuật")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
title = p.add_run("BÁO CÁO THÍ NGHIỆM CUTOFF TRONG MERGESORT")
title.bold = True
title.font.size = Pt(14)

doc.add_heading("Tóm tắt", level=1)
paragraph("Khảo sát ngưỡng chuyển từ mergesort sang insertion sort trên 24 bộ dữ liệu, 12 cutoff và hai phiên đo độc lập, mỗi phiên 7 vòng cho mỗi cấu hình. Mã mergesort do sinh viên gõ lại theo bài giảng, qua 43.230 phép kiểm tra đúng thứ tự và tính ổn định. Theo chỉ số đã định trước, k=7 đứng đầu trong cả hai phiên; k=10 kém k=7 lần lượt 0,45% và 2,14%. Thời gian đo biến động mạnh nên chọn k=7 như giá trị thực dụng trong phạm vi thí nghiệm, chưa chứng minh đó là tối ưu duy nhất.")

doc.add_heading("1. Bài toán và cài đặt", level=1)
paragraph("Giáo trình nhắc cutoff 7 và 10: những đoạn nhỏ có thể được xử lý bằng insertion sort để tránh chi phí đệ quy và merge. Cài đặt top-down dùng Comparable[]; độ dài đoạn là hi - lo + 1. Nếu cutoff > 0 và độ dài không vượt quá cutoff, gọi insertion sort trên đúng đoạn đó; cutoff 0 là mergesort thuần. Khi khóa bằng nhau, lấy phần tử từ nửa trái trước để giữ ổn định. Cả 12 cutoff đều dùng cùng phép kiểm tra bỏ merge nếu cuối nửa trái không lớn hơn đầu nửa phải.")

doc.add_heading("2. Thiết kế và kiểm tra", level=1)
paragraph("Máy đo: Intel Core 5 120U, Windows NT build 26200, Java và javac 25.0.2. Hai phiên bắt đầu lần lượt lúc 22:27 và 22:47 ngày 17/11/2026. Bộ dữ liệu gồm n=10.000 và 100.000; bốn dạng ngẫu nhiên, tăng dần, giảm dần và 8 giá trị lặp; mỗi dạng/kích thước có ba seed cố định. Cả 24 file có SHA-256 khớp giữa hai phiên.")
paragraph("Mỗi bộ dữ liệu được đọc thành Integer[] rồi sắp qua Comparable[]. Trước phép đo, chương trình chạy làm nóng 3 lần cho từng cutoff trên dữ liệu ấy. Trong 7 vòng đo, thứ tự 12 cutoff được xáo mỗi vòng theo seed cố định. Mảng được sao chép trước khi bắt đầu System.nanoTime(); thời gian gồm lời gọi sort và cấp phát aux bên trong sort. Sau khi dừng đồng hồ, kết quả được so với Arrays.sort. Chạy CheckStudent trước mỗi phiên cho kết quả PASS sorted + stable ở 43.230 trường hợp. Hai CSV đều đủ 24 × 12 × 7 = 2.016 dòng, không thiếu hoặc trùng.")
paragraph("Chỉ số chính: với mỗi bộ dữ liệu và cutoff, lấy trung vị 7 thời gian; tính median(k=7) / median(k), sau đó lấy trung bình nhân trên 24 bộ. Chỉ số lớn hơn 1 nghĩa là nhanh hơn k=7. Tổng hợp hai phiên bằng trung bình nhân hai chỉ số phiên. Mỗi bộ dữ liệu và mỗi phiên có trọng số bằng nhau.")

doc.add_page_break()
doc.add_heading("3. Kết quả", level=1)
paragraph("Bảng 1. Chênh lệch tốc độ so với k=7 (%), theo chỉ số chính; số âm nghĩa là chậm hơn.")
table(("k", "Phiên 1", "Phiên 2", "Tổng hợp"),
      [(row["cutoff"], *(f'{float(row[col]):+.2f}'.replace(".", ",") for col in ("run1_pct", "run2_pct", "combined_pct"))) for row in summary],
      (2.0, 4.0, 4.0, 4.0))

doc.add_picture(str(ROOT / "analysis" / "cutoff_two_runs.png"), width=Cm(15.5))
p = doc.paragraphs[-1]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
paragraph("Hình 1. Vùng cutoff 6–16 của hai phiên. Mỗi điểm là trung bình nhân tỉ lệ thời gian sau khi lấy trung vị theo bộ dữ liệu; không phải khoảng tin cậy.")

kind_labels = {"random": "Ngẫu nhiên", "sorted": "Tăng dần", "reverse": "Giảm dần", "few_values": "8 giá trị lặp"}
rows = [row for row in by_kind if row["cutoff"] == "10"]
paragraph("Bảng 2. Riêng k=10 so với k=7 theo dạng đầu vào (%); mỗi nhóm có 6 bộ dữ liệu.")
table(("Dạng đầu vào", "Phiên 1", "Phiên 2"),
      [(kind_labels[row["kind"]], f'{float(row["run1_pct"]):+.2f}'.replace(".", ","), f'{float(row["run2_pct"]):+.2f}'.replace(".", ",")) for row in rows],
      (8.0, 3.0, 3.0))

doc.add_page_break()
doc.add_heading("4. Thảo luận và kết luận", level=1)
paragraph("Theo Bảng 1, k=7 dẫn đầu trong cả hai phiên, còn k=10 đứng sau lần lượt 0,45% và 2,14%; tổng hợp k=10 thấp hơn khoảng 1,30%. Tuy nhiên, k=10 chỉ thắng k=7 trên 11/24 bộ dữ liệu trong từng phiên. Kết quả thay đổi theo dạng đầu vào; chẳng hạn trên dãy đã tăng, k=10 nhanh hơn trong cả hai phiên, còn trên dãy giảm thì chậm hơn.")
paragraph("Tính ổn định còn hạn chế: thời gian trung vị của k=7 ở phiên 2 cao hơn khoảng 25% (trung bình nhân qua 24 bộ) so với phiên 1; có 19 và 47/2.016 thời gian vượt hai lần trung vị của chính cấu hình ở từng phiên. Nếu tính tỉ lệ ghép theo cùng số vòng thay vì tỉ lệ hai trung vị, k=10 lần lượt thành +2,36% và -0,82%; dấu của phiên 1 thay đổi. Chưa ghi tải nền, tần số CPU, trạng thái nhiệt/nguồn; chúng là nguyên nhân có thể, chưa được xác minh. Không coi các sai khác nhỏ là có ý nghĩa thống kê.")
paragraph("Chọn k=7 cho cài đặt và máy đã khảo sát vì đứng đầu theo chỉ số chính ở cả hai phiên; kết luận này chỉ là lựa chọn thực dụng, không phải bằng chứng tối ưu phổ quát. Nếu cần phân biệt các cutoff sát nhau, phải kiểm soát môi trường và đo thêm theo kế hoạch độc lập. Ba CSV của mã cũ và pilot JMH thuộc thí nghiệm khác, không được đưa vào Bảng 1–2.")

doc.add_heading("5. Mã, tài liệu và hỗ trợ AI", level=1)
paragraph("Nguồn thuật toán: slide Mergesort của môn học, các trang 7 (merge), 8 (đệ quy), 18 (insertion cutoff), 20 (bỏ merge nếu đã có thứ tự). Sản phẩm đi kèm: StudentMergeSort.java, CheckStudent.java, GenerateData.java, Benchmark.java, 24 file dữ liệu, hai CSV cùng log/môi trường/hash, script phân tích và đồ thị. Sinh viên gõ các thân hàm sort, merge, insertion, less, exch trong chat theo hướng dẫn; AI chuẩn bị khung, sửa lời gọi less trong merge thành phép compareTo tương đương, bỏ static ở public sort để khớp giao diện, hỗ trợ công cụ đo và báo cáo. Phạm vi hỗ trợ AI được ghi thêm trong AI_USAGE.md.")

output = ROOT / "report" / "Bao_cao_cutoff_25021877_DRAFT.docx"
doc.save(output)
print(output)
