"""
============================================================
  星辰之恋 Mock API - Render.com 服务端
  部署到 Render.com | 无需SSL | HTTP only
============================================================
"""
import json, os, time, uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

# 加载URL映射
with open("url_mapping.json", "r", encoding="utf-8") as f:
    MAP_DATA = json.load(f)

ROUTE_MAP = {}
for route, info in MAP_DATA["mapping"].items():
    ROUTE_MAP[route] = info["handler"]
    print(f"  {route:35s} -> {info['handler']}")

def make_user(uid=1, name="星辰用户"):
    return {
        "id": uid, "username": name, "nickname": name, "avatar": "",
        "is_svip": True, "svip_expire_at": "2099-12-31T23:59:59",
        "user_svip": True, "user_svip_expire": "2099-12-31T23:59:59",
        "user_svip_card_type": "permanent", "svip_card_type": "permanent",
        "token": "mock_" + uuid.uuid4().hex[:8], "diamonds": 999999,
        "is_admin": True, "member_status": "active", "created_at": "2024-01-01T00:00:00",
    }

TRANSPARENT_PNG = bytes.fromhex(
    '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4'
    '890000000a49444154789c62600000000003000105c285020000000049454e44ae426082'
)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # 减少Render日志

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _ok(self, msg="success", extra=None):
        self._json({"code": 0, "message": msg, "data": extra or {}})

    def _read(self):
        cl = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(cl) if cl else b''
        try: return json.loads(body) if body else {}
        except: return {}

    def do_GET(self):
        route = urlparse(self.path).path.rstrip('_')
        handler = ROUTE_MAP.get(route)
        if not handler:
            for k, v in ROUTE_MAP.items():
                if k.rstrip('_') == route:
                    handler = v; break
        handler = handler or "generic"
        print(f"  GET {route} -> {handler}")

        handlers_get = {
            "user_info": lambda: self._ok("ok", make_user()),
            "version": lambda: self._ok("ok", {"version": "9.9.9", "force_update": False}),
            "watermark": lambda: self._ok("ok", {
                "show_watermark": False, "canHideWatermark": True,
                "watermark_text": "", "watermarkHideReason": "svip_user",
                "policy_version": "99", "show_expire_time": False, "enabled": False,
            }),
            "resource": lambda: self._ok("ok", {"resources": [], "categories": [], "total": 0}),
            "feedback": lambda: self._ok("ok", {"posts": [], "total": 0}),
            "danmaku": lambda: self._ok("ok", {"status": "idle"}),
            "parse_quota": lambda: self._ok("ok", {"used": 0, "total": 999}),
            "partner_qr": lambda: self._ok("ok", {"qr_url": ""}),
            "douyin": lambda: self._ok("ok", {"ranking": []}),
            "gift_ico": lambda: self._json({"code": 0, "data": {"icons": []}}),
            "badge_config": lambda: self._json({"badges": []}),
            "api_123pan": lambda: self._json({"data": []}),
            "set_diamonds": lambda: self._ok("ok", {"diamonds": 999999}),
            "ai_chat": lambda: self._ok("ok", {"reply": "你好！"}),
        }
        fn = handlers_get.get(handler)
        if fn:
            fn()
        elif handler == "image":
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(TRANSPARENT_PNG)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(TRANSPARENT_PNG)
        else:
            self._ok("ok")

    def do_POST(self):
        route = urlparse(self.path).path.rstrip('_')
        handler = ROUTE_MAP.get(route)
        if not handler:
            for k, v in ROUTE_MAP.items():
                if k.rstrip('_') == route:
                    handler = v; break
        handler = handler or "generic"
        body = self._read()
        print(f"  POST {route} -> {handler}")

        if handler == "login":
            username = body.get("username", body.get("account", "user"))
            user = make_user(abs(hash(username)) % 9999, username)
            user["token"] = f"mock_{uuid.uuid4().hex[:8]}"
            self._ok("登录成功", {"user": user, "token": user["token"]})
        elif handler == "register":
            username = body.get("username", body.get("account", "new_user"))
            user = make_user(abs(hash(username)) % 9999 + 100, username)
            user["token"] = f"mock_{uuid.uuid4().hex[:8]}"
            self._ok("注册成功", {"user": user, "token": user["token"]})
        elif handler == "send_code":
            self._ok("验证码已发送", {"code": "123456"})
        elif handler == "card_verify":
            self._ok("卡密验证成功", {
                "valid": True, "is_valid": True, "card_type": "permanent",
                "svip_card_type": "permanent", "svip_expire_at": "2099-12-31T23:59:59",
                "expire_at": "2099-12-31T23:59:59", "expires_at": "2099-12-31T23:59:59",
                "user_svip": True, "is_svip": True, "svipExpireAt": "2099-12-31T23:59:59",
            })
        else:
            self._ok("ok")


print("=" * 56)
print("  星辰之恋 Mock API - Render.com")
print(f"  地址: http://xczl.onrender.com")
print("  路由数:", len(ROUTE_MAP))
print("=" * 56)

server = HTTPServer((HOST, PORT), Handler)
print(f"\n  启动在 {HOST}:{PORT} ...")
server.serve_forever()
