# Quản lý ví Ethereum

Script Python này thực hiện các chức năng cơ bản để quản lý ví Ethereum thông qua thư viện web3.py.

## Chức năng

Script thực hiện các chức năng sau:
- Tạo ví Ethereum mới
- Lấy số dư của ví
- Gửi ETH từ một ví đến ví khác
- Kiểm tra trạng thái giao dịch
- Lấy chi tiết giao dịch
- Lưu/đọc thông tin ví
- Tương tác với smart contract (trong file riêng)
- Xem thông tin token ERC-20
- Phân tích giao dịch gần đây của token
- Kiểm tra số dư token của một địa chỉ

## Cài đặt

1. Cài đặt các thư viện yêu cầu:
```
pip install web3 eth-account
```

2. Kết nối đến mạng Ethereum:
   - Script đã được cấu hình với API key Infura
   - Đang kết nối đến mạng thử nghiệm Sepolia để bạn có thể nhận ETH miễn phí

## Cách nhận ETH miễn phí

Vì script kết nối đến mạng thử nghiệm Sepolia, bạn có thể nhận ETH miễn phí từ các faucet sau:

1. **Alchemy Sepolia Faucet**: https://sepoliafaucet.com/
   - Yêu cầu đăng nhập Alchemy
   - Cung cấp 0.5 ETH mỗi ngày

2. **Sepolia PoW Faucet**: https://sepolia-faucet.pk910.de/
   - Đào ETH trên trình duyệt (PoW mining)
   - Không yêu cầu đăng nhập

3. **Faucet chính thức**: https://faucet.sepolia.dev/
   - Yêu cầu Twitter/Social Login
   - Cung cấp lượng ETH nhỏ

## Sử dụng

### 1. Quản lý ví cơ bản

Chạy script quản lý ví:
```
python ethereum_wallet_management.py
```

Script này sẽ:
- Tạo ví mới và lưu thông tin ví vào file `wallet_info.json`
- Hiển thị địa chỉ và số dư ví
- Tạo ví thứ hai để demo giao dịch

Để gửi giao dịch, bạn cần có ETH trong ví:
- Sao chép địa chỉ ví được tạo ra và dán vào một trong các faucet trên để nhận ETH miễn phí
- Sau khi có ETH, bỏ comment đoạn mã gửi giao dịch và chạy lại script

### 2. Tương tác với Smart Contract

Chạy script tương tác với smart contract:
```
python interact_with_smart_contract.py
```

Script này có các chức năng:
- Demo cách tải và tương tác với một smart contract
- Tạo file ABI mẫu cho một token ERC-20
- Hướng dẫn cách gọi các hàm của smart contract
- Xem thông tin chi tiết của token ERC-20 thực tế trên mạng Ethereum
- Phân tích giao dịch gần đây của token
- Kiểm tra số dư token của một địa chỉ

#### Sử dụng tính năng Demo với Token thực tế:

1. Khi chạy script, chọn menu "1. Demo với token thực tế"
2. Chọn một trong ba token có sẵn để xem thông tin
3. Xem thông tin chi tiết của token
4. Xem các giao dịch gần đây của token
5. Nhập địa chỉ để kiểm tra số dư token (bạn có thể dùng địa chỉ mẫu có sẵn)

## Lưu ý

- **KHÔNG BAO GIỜ** chia sẻ private key của bạn
- Script đang kết nối đến mạng thử nghiệm Sepolia, ETH trên mạng này không có giá trị thực
- Đây chỉ là demo với mục đích học tập, bạn có thể thử nghiệm thoải mái trên mạng Sepolia

## Giải quyết sự cố

- Nếu không thể gửi giao dịch, hãy đảm bảo rằng bạn đã có ETH trong ví
- Chúng ta đã khắc phục lỗi với middleware geth_poa_middleware bằng cách thêm xử lý try/except 