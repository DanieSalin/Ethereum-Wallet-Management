#!/usr/bin/env python3
"""
Ethereum Wallet Management
--------------------------
Script để thiết lập và quản lý ví Ethereum sử dụng thư viện web3.py.
"""

import os
import json
from web3 import Web3
import web3
from eth_account import Account
import secrets

# Kết nối đến mạng thử nghiệm Sepolia thay vì mainnet để có thể nhận ETH miễn phí
INFURA_URL = "https://sepolia.infura.io/v3/{URL_INFURA_YOUR_API_KEY}"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Sử dụng middleware cho mạng PoA như Sepolia
try:
    from web3.middleware.geth import geth_poa_middleware
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print("Đã thêm middleware cho mạng PoA")
except ImportError:
    print("Cảnh báo: Không thể import geth_poa_middleware")

# Kiểm tra kết nối
print(f"Đã kết nối đến Ethereum Sepolia: {w3.is_connected()}")
print(f"Phiên bản Web3.py: {web3.__version__}")
print(f"Chain ID: {w3.eth.chain_id}")  # Chain ID của Sepolia là 11155111

def create_wallet():
    """Tạo một ví Ethereum mới và trả về private key và địa chỉ"""
    # Tạo một chuỗi ngẫu nhiên 32 byte để sử dụng làm private key
    private_key = "0x" + secrets.token_hex(32)
    account = Account.from_key(private_key)
    
    print(f"\n--- Đã tạo ví mới ---")
    print(f"Địa chỉ: {account.address}")
    print(f"Private key: {private_key}")
    print("LƯU Ý: KHÔNG CHIA SẺ PRIVATE KEY CỦA BẠN!")
    
    return private_key, account.address

def get_balance(address):
    """Lấy số dư ví (tính bằng Ether)"""
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        
        print(f"\n--- Thông tin ví ---")
        print(f"Địa chỉ: {address}")
        print(f"Số dư: {balance_eth} ETH")
        
        return balance_eth
    except Exception as e:
        print(f"Lỗi khi lấy số dư: {e}")
        return 0

def send_transaction(sender_private_key, recipient_address, amount_eth):
    """Gửi Ether từ ví một sang ví khác"""
    try:
        sender_account = Account.from_key(sender_private_key)
        sender_address = sender_account.address
        
        # Chuyển đổi lượng ETH sang Wei
        amount_wei = w3.to_wei(amount_eth, 'ether')
        
        # Lấy nonce của người gửi
        nonce = w3.eth.get_transaction_count(sender_address)
        
        # Xây dựng giao dịch
        tx = {
            'nonce': nonce,
            'to': recipient_address,
            'value': amount_wei,
            'gas': 21000,  # Giá trị gas tiêu chuẩn cho giao dịch chuyển ETH đơn giản
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        }
        
        # Ký giao dịch
        signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
        
        # Gửi giao dịch đã ký
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"\n--- Gửi giao dịch ---")
        print(f"Từ: {sender_address}")
        print(f"Đến: {recipient_address}")
        print(f"Số lượng: {amount_eth} ETH")
        print(f"Hash giao dịch: {tx_hash.hex()}")
        
        return tx_hash.hex()
    except Exception as e:
        print(f"Lỗi khi gửi giao dịch: {e}")
        return None

def check_transaction_status(tx_hash):
    """Kiểm tra trạng thái của một giao dịch"""
    try:
        # Đợi giao dịch được xác nhận
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        status = "Thành công" if tx_receipt.status == 1 else "Thất bại"
        
        print(f"\n--- Trạng thái giao dịch ---")
        print(f"Hash giao dịch: {tx_hash}")
        print(f"Trạng thái: {status}")
        print(f"Block: {tx_receipt.blockNumber}")
        print(f"Gas đã sử dụng: {tx_receipt.gasUsed}")
        
        return tx_receipt
    except Exception as e:
        print(f"Lỗi khi kiểm tra giao dịch: {e}")
        return None

def save_wallet_info(private_key, address, filename="wallet_info.json"):
    """Lưu thông tin ví vào một file JSON"""
    wallet_info = {
        "address": address,
        "private_key": private_key
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(wallet_info, f)
        
        print(f"\nĐã lưu thông tin ví vào {filename}")
    except Exception as e:
        print(f"Lỗi khi lưu thông tin ví: {e}")

def load_wallet_info(filename="wallet_info.json"):
    """Đọc thông tin ví từ một file JSON"""
    try:
        with open(filename, 'r') as f:
            wallet_info = json.load(f)
        return wallet_info.get("private_key"), wallet_info.get("address")
    except FileNotFoundError:
        print(f"Không tìm thấy file {filename}")
        return None, None
    except Exception as e:
        print(f"Lỗi khi đọc thông tin ví: {e}")
        return None, None

def get_transaction_details(tx_hash):
    """Lấy chi tiết của một giao dịch"""
    try:
        tx = w3.eth.get_transaction(tx_hash)
        
        print(f"\n--- Chi tiết giao dịch ---")
        print(f"Hash: {tx_hash}")
        print(f"Từ: {tx['from']}")
        print(f"Đến: {tx['to']}")
        print(f"Giá trị: {w3.from_wei(tx['value'], 'ether')} ETH")
        print(f"Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
        print(f"Nonce: {tx['nonce']}")
        
        if tx.blockNumber is not None:
            block = w3.eth.get_block(tx.blockNumber)
            print(f"Thời gian: {block.timestamp}")
        
        return tx
    except Exception as e:
        print(f"Lỗi khi lấy chi tiết giao dịch: {e}")
        return None

def main():
    print("=== QUẢN LÝ VÍ ETHEREUM ===\n")
    
    # Tạo ví mới
    private_key, address = create_wallet()
    
    # Lưu thông tin ví
    save_wallet_info(private_key, address, "wallet_info.json")
    
    # Kiểm tra số dư
    balance = get_balance(address)
    
    print("\nLƯU Ý: Để gửi giao dịch, bạn cần có ETH trong ví của mình.")
    print("Bạn đang sử dụng mạng thử nghiệm Sepolia, bạn có thể nhận ETH miễn phí từ các faucet sau:")
    print("1. https://sepoliafaucet.com/ - Yêu cầu đăng nhập Alchemy")
    print("2. https://sepolia-faucet.pk910.de/ - Faucet PoW (đào trên trình duyệt)")
    print("3. https://faucet.sepolia.dev/ - Faucet chính thức")
    print("\nHãy sao chép địa chỉ ví của bạn và dán vào một trong các faucet trên để nhận ETH miễn phí.")
    
    # Demo: Tạo ví thứ hai
    print("\nTạo ví thứ hai để demo giao dịch:")
    second_private_key, second_address = create_wallet()
    
    # Kiểm tra xem người dùng có ETH không trước khi gửi giao dịch
    if balance > 0:
        print("\nVí của bạn có ETH, thực hiện gửi giao dịch...")
        
        # Gửi một giao dịch
        tx_hash = send_transaction(private_key, second_address, 0.001)
        
        if tx_hash:
            # Kiểm tra trạng thái giao dịch
            tx_receipt = check_transaction_status(tx_hash)
            
            # Hiển thị chi tiết giao dịch
            tx_details = get_transaction_details(tx_hash)
            
            # Kiểm tra số dư sau giao dịch
            print("\nSố dư sau giao dịch:")
            get_balance(address)
            get_balance(second_address)
    else:
        print("\nVí của bạn chưa có ETH. Để thực hiện giao dịch:")
        print("1. Sao chép địa chỉ ví của bạn: " + address)
        print("2. Truy cập một trong các faucet được đề xuất ở trên")
        print("3. Nhận ETH miễn phí")
        print("4. Chạy lại script này để thực hiện giao dịch")
        
        # Vẫn hiển thị số dư hiện tại
        print("\nSố dư hiện tại:")
        get_balance(address)
        get_balance(second_address)

if __name__ == "__main__":
    main() 