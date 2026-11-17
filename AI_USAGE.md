# Ghi nhận hỗ trợ AI

Bài giảng Mergesort của môn học được dùng làm nguồn cho cài đặt thuật toán. Sinh viên đã tự gõ thân các hàm `merge`, `sort` đệ quy, `insertion`, `less`, `exch` và hàm `sort` công khai trong cuộc trao đổi với AI. AI hướng dẫn từng bước, chuẩn bị cấu trúc dự án, kiểm thử, bộ dữ liệu, công cụ đo, phân tích và soạn báo cáo. Để ghép mã vào giao diện `SortAlgorithm`, AI đổi `less(aux[j], aux[i])` trong `merge` thành phép so sánh tương đương `aux[j].compareTo(aux[i]) < 0`, và đổi `public static sort` thành phương thức thể hiện. Hai phiên đo dùng đúng tệp `src/StudentMergeSort.java` hiện có; bản sao và SHA-256 nằm trong `results/run1/` và `results/run2/`.

AI giúp diễn giải kết quả; lựa chọn k=7 theo chỉ số mô tả không chứng minh ngưỡng tối ưu trên mọi máy. Không trộn số liệu pilot JMH hoặc các bản mã cũ vào hai phiên này.

Ảnh đề gốc liệt kê “log chat với AI (nếu có)”. Sinh viên cho biết giảng viên đã nói lịch sử chat không bắt buộc; tệp này ghi minh bạch phạm vi hỗ trợ AI trong sản phẩm nộp. Nếu giảng viên yêu cầu log riêng, có thể bổ sung liên kết hoặc bản xuất khi đó.