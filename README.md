# Trạng thái cảnh báo vùng mua

Nhánh này không chứa code và không chứa bí mật.

`state/buy_zones.json` chỉ lưu cờ đã báo / chưa báo: id trang Notion, đang ở trong vùng hay không, mức vô hiệu đã báo, ngày bản tin sáng, và id CoinGecko.

Không có token Telegram, không có Notion token, không có ghi chú phân tích.

GitHub Actions cập nhật file này mỗi lần chạy để không báo trùng sau khi runner tắt.
Cache của GitHub Actions có thể bị xóa sau vài ngày không dùng, nên không dùng cache cho việc này.
