#!/usr/bin/env python3
"""
Tương tác với Smart Contract Ethereum
------------------------------------
Script để tương tác với các smart contract trên mạng Ethereum.
"""

import json
from web3 import Web3
import web3
from eth_account import Account

# Kết nối đến mạng thử nghiệm Sepolia thay vì mainnet
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

def load_contract(contract_address, abi_file):
    """Tải một smart contract để tương tác"""
    try:
        # Đọc ABI từ file
        with open(abi_file, 'r') as f:
            contract_abi = json.load(f)
        
        # Tạo đối tượng contract
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        return contract
    except Exception as e:
        print(f"Lỗi khi tải contract: {e}")
        return None

def call_contract_function(contract, function_name, *args):
    """Gọi một hàm view/pure của smart contract"""
    try:
        # Lấy hàm từ contract
        contract_function = getattr(contract.functions, function_name)
        
        # Gọi hàm với các tham số
        result = contract_function(*args).call()
        
        print(f"\n--- Gọi hàm {function_name} ---")
        print(f"Tham số: {args}")
        print(f"Kết quả: {result}")
        
        return result
    except Exception as e:
        print(f"Lỗi khi gọi hàm {function_name}: {e}")
        return None

def send_contract_transaction(contract, private_key, function_name, *args):
    """Gửi giao dịch đến một hàm của smart contract"""
    try:
        # Lấy thông tin tài khoản từ private key
        account = Account.from_key(private_key)
        sender_address = account.address
        
        # Lấy hàm từ contract
        contract_function = getattr(contract.functions, function_name)
        
        # Xây dựng giao dịch
        transaction = contract_function(*args).build_transaction({
            'from': sender_address,
            'nonce': w3.eth.get_transaction_count(sender_address),
            'gas': 2000000,  # Giá trị gas tối đa, có thể điều chỉnh
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        })
        
        # Ký giao dịch
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Gửi giao dịch đã ký
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"\n--- Gửi giao dịch đến hàm {function_name} ---")
        print(f"Tham số: {args}")
        print(f"Từ: {sender_address}")
        print(f"Hash giao dịch: {tx_hash.hex()}")
        
        return tx_hash.hex()
    except Exception as e:
        print(f"Lỗi khi gửi giao dịch đến hàm {function_name}: {e}")
        return None

def get_contract_events(contract, event_name, from_block=0, to_block='latest'):
    """Lấy các sự kiện từ smart contract"""
    try:
        # Lấy sự kiện từ contract
        event_filter = getattr(contract.events, event_name).create_filter(
            fromBlock=from_block, 
            toBlock=to_block
        )
        
        # Lấy tất cả các entries
        events = event_filter.get_all_entries()
        
        print(f"\n--- Các sự kiện {event_name} ---")
        for i, event in enumerate(events):
            print(f"Event {i+1}:")
            print(f"  Block: {event.blockNumber}")
            print(f"  Transaction: {event.transactionHash.hex()}")
            print(f"  Args: {event.args}")
        
        return events
    except Exception as e:
        print(f"Lỗi khi lấy sự kiện {event_name}: {e}")
        return []

def deploy_contract(private_key, contract_bytecode, contract_abi, *constructor_args):
    """Triển khai một smart contract mới"""
    try:
        # Lấy thông tin tài khoản từ private key
        account = Account.from_key(private_key)
        sender_address = account.address
        
        # Tạo đối tượng contract
        contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        
        # Xây dựng giao dịch triển khai
        transaction = contract.constructor(*constructor_args).build_transaction({
            'from': sender_address,
            'nonce': w3.eth.get_transaction_count(sender_address),
            'gas': 3000000,  # Gas tối đa cho việc triển khai
            'gasPrice': w3.eth.gas_price,
            'chainId': w3.eth.chain_id
        })
        
        # Ký giao dịch
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
        
        # Gửi giao dịch đã ký
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"\n--- Triển khai smart contract ---")
        print(f"Từ: {sender_address}")
        print(f"Hash giao dịch: {tx_hash.hex()}")
        
        # Đợi giao dịch được xác nhận
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        
        print(f"Địa chỉ contract: {contract_address}")
        return contract_address
    except Exception as e:
        print(f"Lỗi khi triển khai contract: {e}")
        return None

def get_token_info(token_address):
    """Lấy thông tin cơ bản của một token ERC-20"""
    # ABI tối thiểu cho ERC-20
    erc20_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    try:
        # Tạo contract instance
        token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)
        
        # Lấy thông tin token
        name = token_contract.functions.name().call()
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
        total_supply = token_contract.functions.totalSupply().call() / (10 ** decimals)
        
        print(f"\n--- Thông tin Token ERC-20 ---")
        print(f"Địa chỉ: {token_address}")
        print(f"Tên: {name}")
        print(f"Ký hiệu: {symbol}")
        print(f"Số thập phân: {decimals}")
        print(f"Tổng cung: {total_supply} {symbol}")
        
        return {
            "address": token_address,
            "name": name,
            "symbol": symbol,
            "decimals": decimals,
            "total_supply": total_supply
        }
    except Exception as e:
        print(f"Lỗi khi lấy thông tin token: {e}")
        return None

def analyze_token_transactions(token_address, num_transactions=5):
    """Phân tích giao dịch gần đây của một token ERC-20"""
    # ABI cho sự kiện Transfer của ERC-20
    transfer_event_abi = {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
    
    try:
        # Thay vì sử dụng filter, chúng ta sẽ lấy một giao dịch gần đây bằng cách kiểm tra block hiện tại
        latest_block = w3.eth.block_number
        print(f"\n--- Giao dịch gần đây của token ---")
        print(f"Block hiện tại: {latest_block}")
        print("Lưu ý: Chức năng này có giới hạn trên API Infura, không hiển thị được giao dịch.")
        print("Để xem giao dịch gần đây của token, bạn có thể sử dụng Etherscan:")
        print(f"https://etherscan.io/token/{token_address}")
        
        return []
    except Exception as e:
        print(f"Lỗi khi phân tích giao dịch token: {e}")
        return []

def demo_with_real_token():
    """Demo tương tác với một token ERC-20 thực tế trên mạng Ethereum"""
    # Địa chỉ của một số token phổ biến trên Sepolia
    # Lưu ý: Các địa chỉ này có thể khác với mainnet
    tokens = {
        "Sepolia ETH Wrapped (WETH)": "0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9",
        "Sepolia USDC": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
        "DAI clone": "0x3e622317f8C93f7328350cF0B56d9eD4C620C5d6",
        "BNB": "0x46EdAE270490c050D9c77b18d91BA1b837528c05"  # Địa chỉ BNB token
    }
    
    print("\n=== Demo với Token trên Sepolia ===")
    print("Chọn một token để xem thông tin:")
    
    for i, (name, address) in enumerate(tokens.items(), 1):
        print(f"{i}. {name} ({address})")
    
    choice = input("\nNhập số (1-4) hoặc nhấn Enter để chọn WETH: ")
    
    if not choice:
        choice = "1"
    
    try:
        index = int(choice) - 1
        selected_token = list(tokens.keys())[index]
        token_address = tokens[selected_token]
        
        print(f"\nĐã chọn token: {selected_token}")
        
        # Lấy thông tin token
        token_info = get_token_info(token_address)
        
        if token_info:
            # Phân tích giao dịch gần đây
            analyze_token_transactions(token_address, 3)
            
            # Kiểm tra số dư token của một địa chỉ
            print("\nNhập địa chỉ ví để kiểm tra số dư token")
            print("Địa chỉ Ethereum hợp lệ có dạng: 0x... (42 ký tự)")
            print("Ví dụ: 0x375B497D962A8771b89B2a55712a3755D6d68B36")
            
            # Thêm một số ví mẫu để người dùng có thể sao chép
            sample_addresses = [
                "0x375B497D962A8771b89B2a55712a3755D6d68B36",  # Địa chỉ từ wallet_info.json
                "0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9",  # Địa chỉ WETH trên Sepolia
                "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"   # Địa chỉ USDC trên Sepolia
            ]
            print("\nBạn có thể dùng một trong các địa chỉ mẫu sau:")
            for i, addr in enumerate(sample_addresses):
                print(f"{i+1}. {addr}")
            
            address_to_check = input("\nNhập địa chỉ hoặc nhấn Enter để bỏ qua: ")
            
            if not address_to_check:
                print("Đã bỏ qua kiểm tra số dư.")
                return
            
            # Kiểm tra định dạng địa chỉ
            if not address_to_check.startswith('0x'):
                address_to_check = '0x' + address_to_check
            
            try:
                # Sử dụng hàm to_checksum_address của web3.py để chuyển đổi địa chỉ
                checksum_address = Web3.to_checksum_address(address_to_check)
                
                token_contract = w3.eth.contract(address=token_address, abi=[
                    {
                        "constant": True,
                        "inputs": [{"name": "_owner", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "balance", "type": "uint256"}],
                        "payable": False,
                        "stateMutability": "view",
                        "type": "function"
                    }
                ])
                
                balance = token_contract.functions.balanceOf(checksum_address).call()
                decimals = token_info["decimals"]
                balance_formatted = balance / (10 ** decimals)
                
                print(f"\n--- Số dư Token ---")
                print(f"Địa chỉ: {checksum_address}")
                print(f"Số dư: {balance_formatted} {token_info['symbol']}")
            
            except ValueError:
                print(f"Địa chỉ không hợp lệ: {address_to_check}")
                print("Địa chỉ Ethereum phải có 42 ký tự, bắt đầu bằng 0x và chỉ chứa các ký tự hex (0-9, a-f).")
            except Exception as e:
                print(f"Lỗi khi kiểm tra số dư: {e}")
    except Exception as e:
        print(f"Lỗi: {e}")

def main():
    print("=== TƯƠNG TÁC VỚI SMART CONTRACT ETHEREUM ===\n")
    
    # Ví dụ ABI của một ERC-20 token đơn giản
    sample_erc20_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "symbol",
            "outputs": [{"name": "", "type": "string"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    print("\nVí dụ cách sử dụng:")
    print("1. Lưu ABI vào một file JSON")
    
    try:
        with open("erc20_abi.json", "w") as f:
            json.dump(sample_erc20_abi, f)
        
        print("   Đã lưu ABI vào file erc20_abi.json")
    except Exception as e:
        print(f"   Lỗi khi lưu ABI: {e}")
    
    print("2. Tải contract (cần địa chỉ contract thực tế):")
    print("   contract = load_contract('0x...', 'erc20_abi.json')")
    
    print("3. Gọi hàm view:")
    print("   name = call_contract_function(contract, 'name')")
    
    print("4. Gửi giao dịch (cần private key và ETH trong tài khoản):")
    print("   tx_hash = send_contract_transaction(contract, private_key, 'transfer', recipient_address, amount)")
    
    print("\nLưu ý: Để thực hiện ví dụ trên, bạn cần thay thế địa chỉ contract, private key và các tham số khác bằng giá trị thực.")
    
    print("\n--- Menu ---")
    print("1. Demo với token thực tế")
    print("2. Thoát")
    
    choice = input("\nLựa chọn của bạn (1-2): ")
    
    if choice == "1":
        demo_with_real_token()
    else:
        print("Tạm biệt!")

if __name__ == "__main__":
    main() 