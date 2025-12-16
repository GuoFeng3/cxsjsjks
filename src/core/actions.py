import random
import json
import os
from typing import Dict, List, Any

# Global Data Storage
orders: Dict[str, str] = {}
users: Dict[str, Dict[str, Any]] = {}
USER_FILE = os.path.join(os.getcwd(), "data", "userinfo.txt")

def load_users():
    """Loads users from the file if it exists."""
    global users
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r', encoding='utf-8') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            print("Warning: Corrupt user file, starting with empty users.")
            users = {}
    else:
        users = {}

def save_users():
    """Saves users to the file."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    with open(USER_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# Initial load
load_users()

def place_order(context: Dict[str, Any], args: List[str]):
    """
    Places an order.
    Args:
        context: The interpreter context.
        args: List of arguments, expects prefix as the first argument.
    """
    if not args:
        print("Error: place_order requires a prefix argument.")
        return

    prefix = args[0]
    item_name = context.get("last_intent", "Unknown")
    order_id = f"{prefix}-" + "".join([str(random.randint(0, 9)) for _ in range(6)])
    orders[order_id] = item_name
    context["last_order_id"] = order_id

def check_order_from_input(context: Dict[str, Any], args: List[str]):
    """
    Checks an order status.
    Args:
        context: The interpreter context.
        args: List of arguments, optionally the source of the order ID.
    """
    source = args[0] if args else "user_input"
    
    if source == "user_input":
        order_id = context.get("last_user_input", "")
    else:
        order_id = source
        
    if order_id in orders:
        context["check_result"] = f"订单号：{order_id}，内容：{orders[order_id]}"
    else:
        context["check_result"] = "未查询到该订单"

def user_login(context: Dict[str, Any], args: List[str]):
    """
    Logs in a user.
    Args:
        context: The interpreter context.
        args: Source of username, usually "user_input".
    """
    source = args[0] if args else "user_input"
    
    if source == "user_input":
        username = context.get("last_user_input", "")
    else:
        username = source
        
    if not username:
        print("Warning: Empty username provided for login.")
        return

    context["username"] = username
    
    # Reload to ensure we have latest data
    load_users()
    
    # Create user if not exists
    if username not in users:
        users[username] = {"balance": 0.0, "data": 0.0, "combo": ""}
        save_users()
    
    print(f"好的，我知道了")

def charge_bill(context: Dict[str, Any], args: List[str]):
    """
    Charges phone bill.
    Args:
        context: Interpreter context
        args: Source of amount, usually "user_input"
    """
    username = context.get("username")
    if not username or username not in users:
        print("Error: User not logged in.")
        return

    source = args[0] if args else "user_input"
    if source == "user_input":
        amount_str = context.get("last_user_input", "0")
    else:
        amount_str = source
    
    try:
        amount = float(amount_str)
        users[username]["balance"] += amount
        save_users()
        print(f"Robot: 用户 {username} 充值了 {amount}. 新的余额为: {users[username]['balance']}")
    except ValueError:
        print(f"Error: Invalid amount '{amount_str}'")

def charge_data(context: Dict[str, Any], args: List[str]):
    """
    Charges data (flow).
    Args:
        context: Interpreter context
        args: Source of amount, usually "user_input"
    """
    username = context.get("username")
    if not username or username not in users:
        print("Error: User not logged in.")
        return

    source = args[0] if args else "user_input"
    if source == "user_input":
        amount_str = context.get("last_user_input", "0")
    else:
        amount_str = source
    
    try:
        amount = float(amount_str)
        users[username]["data"] += amount
        save_users()
        print(f"Robot: 用户 {username} 充值了 {amount}GB 数据. 新的流量为: {users[username]['data']}GB")
    except ValueError:
        print(f"Error: Invalid data amount '{amount_str}'")

def change_combo(context: Dict[str, Any], args: List[str]):
    """
    Changes user combo.
    Args:
        context: Interpreter context
        args: Source of combo name, usually "last_intent" (since it comes from a branch choice)
    """
    username = context.get("username")
    if not username or username not in users:
        print("Error: User not logged in.")
        return

    combo = context.get("last_intent")
    if not combo or "套餐" not in combo:
         combo = context.get("last_user_input")
         
    if combo:
        users[username]["combo"] = combo
        save_users()
        print(f"Robot: 用户 {username} 更改为套餐 {combo}")
    else:
        print("Error: Could not determine new combo.")

def check_status(context: Dict[str, Any], args: List[str]):
    """
    Checks user status (balance, data, combo).
    Populates context["check_result"].
    """
    username = context.get("username")
    if not username or username not in users:
        context["check_result"] = "用户未登录"
        return

    user_data = users[username]
    msg = (f"当前话费余额：{user_data['balance']}元，"
           f"剩余流量：{user_data['data']}GB，"
           f"当前套餐：{user_data['combo']}")
    context["check_result"] = msg
