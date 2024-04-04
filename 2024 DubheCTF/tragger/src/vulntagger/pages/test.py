import hashlib

# 假设给定的盐值和哈希密码
PASSWORD_SALT = "subscribe_taffy_thanks_meow!"
SALTED_PASSWORD = "52bf037e335053f2f229cfe0f1924a903ca8372d4d9a36522a8ccbc03cb7b3fc"  # 例子中的哈希密码

# 假设凭据对象
class Credentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# 正确的管理员用户名和密码
admin_credentials = Credentials("admin", "strongpassword123")

# 验证凭据
def compare_digest(a, b):
    # 实际开发中应该使用安全的比较函数，例如 cryptography 模块的 compare_digest
    return a == b

if (
    compare_digest(admin_credentials.username, "admin")
    and compare_digest(
        hashlib.sha256(
            f"{PASSWORD_SALT}{admin_credentials.password}{PASSWORD_SALT}".encode()
        ).hexdigest(),
        SALTED_PASSWORD,
    )
):
    print("凭据验证成功！")
else:
    print("凭据验证失败！")
