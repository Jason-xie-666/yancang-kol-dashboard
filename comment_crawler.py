"""
comment_crawler.py — 小红书评论爬取模块
支持两种模式：
- demo=True:  返回模拟数据，面试演示用（无需 Cookie）
- demo=False: 真实爬取，基于 DrissionPage + Edge 浏览器

统一接口：fetch_comments(note_url, count=50, demo=True) -> list[str]
"""

import os
import re
import time


# ============================================================
# 配置
# ============================================================
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_COOKIE_PATH = os.path.join(_BASE_DIR, "cookie.txt")
_EDGE_PATH = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"


def _load_cookie() -> str:
    """从 cookie.txt 读取小红书 Cookie"""
    if not os.path.exists(_COOKIE_PATH):
        return ""
    with open(_COOKIE_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _extract_note_id(url_or_id: str) -> str:
    """从 URL 提取 note_id"""
    match = re.search(r"(?:explore|item|note)[=/](\w+)", url_or_id)
    if match:
        return match.group(1)
    if re.fullmatch(r"[a-zA-Z0-9_]{10,}", url_or_id):
        return url_or_id
    raise ValueError(f"无法提取 note_id：{url_or_id}")


# ============================================================
# Demo 数据：模拟言仓笔记的真实评论（面试演示用）
# ============================================================
_DEMO_COMMENTS = [
    # 正面-治愈感
    "这个日历太治愈了吧，每天翻开都是不一样的惊喜",
    "线条小狗真的太太太可爱了！谁懂啊！！",
    "放在办公桌上，同事路过都要问链接，已经被种草三个人了",
    "收到货就被包装惊艳到了，言仓真的每个细节都用心",
    "买给闺蜜的生日礼物，她拆开的时候眼眶都红了",
    "男朋友说这是我送过最有意义的礼物，比口红香水强一百倍",
    "上次那个坏心情急救包我到现在还在用，每次不开心就翻一翻",
    "这个纸质真的绝了，摸上去很厚实，撕下来还能当便签用",
    "从言仓刚开店就关注了，每一款产品都长在我的审美上",
    "已经买了第三个送人了，朋友说我是言仓野生代言人",
    "每天翻日历的时候都觉得生活好像没那么糟糕了",
    "小刘鸭那个压力诊断单，测出重度摸鱼患者，笑着笑着就哭了",

    # 中性-问价格/询问产品
    "这个有小狗音箱那一款吗？想买个配套的",
    "问一下姐妹们这个日历是每天一张还是一周一页呀？",
    "能不能单独买那个贴纸啊，日历我有了就想要贴纸",
    "学生党想问一下这个活动到什么时候",
    "跟旅行日历比哪个更推荐呀？纠结中",
    "姐妹这个狗狗是印刷的还是手绘上去的质感呀",
    "刚下单了一本，蹲蹲看实物怎么样",
    "请问这个金属环会生锈吗？南方潮湿有点担心",
    "第一次买言仓的东西，大家觉得哪个最值得入手？",

    # 中性偏负
    "收到了，好看是好看，但是69有点小贵说实话",
    "日历纸质没有我想象的好，撕的时候容易破",
    "能不能出个便宜点的平替版，学生党伤不起",
    "为什么我的小狗耳朵那里有点掉色了，是品控问题吗",
    "包装好是好，但感觉过度包装了，不够环保",
    "不太适合男生说实话，买给男朋友他get不到",
    "这个能不能7天无理由？收到感觉跟图片有点色差",
    "快递盒压坏了，虽然有包装保护但还是有点心疼",
    "觉得这款没有去年的线条小狗日历好看，今年配色有点暗",

    # 正面-使用场景
    "每天早上打卡一样翻一页，已经坚持三个月了",
    "旅行日历背面写日记真的超合适，每天写一点心情",
    "做了个开箱视频，点赞过千了哈哈哈，言仓快打钱",
    "把这个和坏心情急救包搭配用，简直是情绪自救组合",
    "买了三个，桌面一个床边一个送朋友一个，三倍的快乐",
    "小狗音箱当小夜灯太合适了，灯光暖暖的不刺眼",
    "考研党每天看一页旅行日历，幻想考完就去这些地方",
    "上班摸鱼的时候翻一翻日历，感觉灵魂已经去度假了",
    "把撕下来的日历贴在手账本上，一整本都是小狗狗",
    "冬天抱着水豚噜噜毛毯，再翻着日历，幸福感拉满",

    # 更多好评
    "在直播间买的比店里便宜十块钱还送贴纸，赚了赚了",
    "这个设计师肯定很懂生活，每个小细节都想让人哭",
    "比起那些大牌日历，这个真的有灵魂，不是冷冰冰的功能品",
    "言仓的东西就是那种——你会忍不住想分享给所有人的好",
    "姐妹们都去买！不是广！是真的好！(虽然我这样说很像广)",
    "搬家的时候把旧的言仓日历弄丢了，心疼了好几个月",
    "上次考试周压力大到崩溃，就是靠着坏心情急救包撑过来的",
    "期待言仓和更多IP联名！线条小狗之后能不能出Chiikawa！",
    "我妈看到我桌上这个日历都说现在的文具做得真好看",
    "给即将出国留学的闺蜜送了旅行日历，她说想家就翻一页",
]


def manual_import(comments_text: str) -> list:
    """
    手动粘贴评论：用户从浏览器直接复制评论区的文字，粘贴进来。
    支持两种分隔方式：
      - 每行一条评论
      - 数字编号开头（如 "1. xxx"、"1、xxx"）

    参数：
        comments_text (str): 用户粘贴的评论文本（多行）
    返回：
        list[str]: 清洗后的评论列表
    """
    import re
    result = []
    for line in comments_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # 去掉编号前缀 "1.", "1、", "1)", "评论1:" 等
        line = re.sub(r"^[\d]+[\.\、\)\s\:\：\-]+", "", line).strip()
        if len(line) >= 3:  # 至少 3 个字符
            result.append(line)
    return result if result else ["未能解析评论，请每行粘贴一条评论"]


def _get_demo_comments(count: int = 50) -> list:
    """返回模拟评论数据，循环使用 _DEMO_COMMENTS 直到达到目标数量"""
    if count <= len(_DEMO_COMMENTS):
        return _DEMO_COMMENTS[:count]
    # 超过 demo 数据量就循环
    repeats = (count // len(_DEMO_COMMENTS)) + 1
    return (_DEMO_COMMENTS * repeats)[:count]


# ============================================================
# 真实爬取（demo=False 时使用）
# ============================================================
def _fetch_real(note_url: str, note_id: str, cookie_str: str, count: int) -> list:
    """使用 DrissionPage + Edge 真实爬取评论"""
    try:
        from DrissionPage import ChromiumPage, ChromiumOptions
    except ImportError:
        print("[Error] DrissionPage not installed. Run: pip install DrissionPage")
        return ["爬取失败，请检查Cookie和链接"]

    # 解析 cookie
    cookies_dict = {}
    for item in cookie_str.split(";"):
        item = item.strip()
        if "=" in item:
            k, _, v = item.partition("=")
            cookies_dict[k.strip()] = v.strip()

    full_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    page = None

    try:
        co = ChromiumOptions()
        co.set_browser_path(_EDGE_PATH)
        co.headless(False)
        co.set_argument("--no-sandbox")
        co.set_argument("--disable-blink-features=AutomationControlled")
        co.set_argument("--window-size=1400,900")
        page = ChromiumPage(co)

        # 注入 Cookie
        page.get("https://www.xiaohongshu.com")
        time.sleep(2)
        for name, value in cookies_dict.items():
            try:
                page.set.cookies(name, value)
            except Exception:
                pass

        # 访问笔记
        page.get(full_url)
        time.sleep(5)

        # 如果跳到登录/错误页，尝试等待用户手动登录
        current_url = page.url
        if "login" in current_url.lower() or "error" in current_url.lower():
            print("[Info] Login page detected. You have 30s to scan QR in the browser...")
            time.sleep(30)
            page.get(full_url)
            time.sleep(5)

        # 提取评论
        comments = []
        seen = set()
        max_scrolls = 40
        skip_kw = ["评论", "赞", "收藏", "分享", "关注", "举报", "登录", "扫码",
                    "打开App", "说点什么", "添加评论", "查看更多", "打开小红书"]

        for scroll in range(max_scrolls):
            try:
                els = page.eles("tag:span", timeout=2)
                for el in els:
                    try:
                        text = el.text.strip()
                    except Exception:
                        continue
                    if 4 < len(text) < 500 and text not in seen:
                        if not any(kw in text for kw in skip_kw):
                            seen.add(text)
                            comments.append(text)
                            if len(comments) >= count:
                                break
                page.scroll.down(600)
                time.sleep(1)
                if len(comments) >= count:
                    break
                if scroll % 5 == 0:
                    print(f"[Progress] {len(comments)}/{count}")
            except Exception:
                continue

        return comments[:count] if comments else ["爬取失败，请检查Cookie和链接"]

    except Exception as e:
        print(f"[Browser error] {e}")
        return ["爬取失败，请检查Cookie和链接"]
    finally:
        if page:
            try:
                page.quit()
            except Exception:
                pass


# ============================================================
# 统一入口
# ============================================================
def fetch_comments(note_url: str, count: int = 50, demo: bool = True) -> list:
    """
    爬取小红书单篇笔记的评论内容。

    参数：
        note_url (str): 小红书笔记链接或 note_id
        count  (int) : 需要爬取的评论数（默认 50）
        demo   (bool): True=模拟数据（面试演示），False=真实爬取
    返回：
        list[str]: 每条评论为纯文本字符串
        失败时返回 ["爬取失败，请检查Cookie和链接"]
    """
    # --- Demo 模式：直接返回模拟数据 ---
    if demo:
        print(f"[Demo] Returning {count} simulated comments for demo")
        return _get_demo_comments(count)

    # --- 真实模式 ---
    try:
        note_id = _extract_note_id(note_url)
    except ValueError as e:
        print(f"[URL error] {e}")
        return ["爬取失败，请检查Cookie和链接"]

    cookie_str = _load_cookie()
    if not cookie_str:
        print("[Cookie error] cookie.txt is empty or not found")
        return ["爬取失败，请检查Cookie和链接"]

    return _fetch_real(note_url, note_id, cookie_str, count)


# ============================================================
# 模块自测
# ============================================================
if __name__ == "__main__":
    test_url = "https://www.xiaohongshu.com/explore/665f8a3b000000001b03d2a9"

    print("=" * 60)
    print("[TEST] comment_crawler.py Self-Test")
    print("=" * 60)

    # --- 测试 demo 模式 ---
    print("\n--- Demo Mode ---")
    comments = fetch_comments(test_url, count=10, demo=True)
    print(f"Got {len(comments)} comments (demo)")
    for i, c in enumerate(comments[:5], 1):
        print(f"  {i}. {c[:100]}{'...' if len(c) > 100 else ''}")

    # --- 测试真实模式（需要 Cookie） ---
    print("\n--- Real Mode ---")
    cookie = _load_cookie()
    if cookie:
        print(f"Cookie found ({len(cookie)} chars), trying real scrape...")
        comments = fetch_comments(test_url, count=50, demo=False)
        if comments and comments[0] != "爬取失败，请检查Cookie和链接":
            print(f"Got {len(comments)} real comments!")
            for i, c in enumerate(comments[:3], 1):
                clean = c.replace("\n", " ").strip()
                print(f"  {i}. {clean[:120]}...")
        else:
            print(f"Real scrape failed: {comments[0]}")
            print("(This is expected — Xiaohongshu has strong anti-bot protection)")
            print("Use demo=True for interview presentation.")
    else:
        print("No cookie found. Real mode requires valid Xiaohongshu cookie.")
        print("Use demo=True for interview presentation.")

    print("\n" + "=" * 60)
    print("[DONE] comment_crawler.py test complete")
