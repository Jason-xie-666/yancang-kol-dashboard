"""
言仓文创 KOL 内容品控 & 复盘工作台 —— AI 工具模块
所有函数调用 DeepSeek V4 API，统一异常处理。
"""

import os
import json
from openai import OpenAI

# ============================================================
# 全局配置：DeepSeek API 客户端
# ============================================================
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"  # DeepSeek V4 最新模型

# 先确定项目目录（后续加载文件也需要）
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 多来源加载 API Key（优先级：系统环境变量 > API.txt > .env）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

if not DEEPSEEK_API_KEY:
    # 尝试从桌面 API.txt 读取
    _api_txt = os.path.join(os.path.expanduser("~"), "Desktop", "API.txt")
    if os.path.exists(_api_txt):
        with open(_api_txt, "r", encoding="utf-8") as _f:
            DEEPSEEK_API_KEY = _f.read().strip()

if not DEEPSEEK_API_KEY:
    # 尝试从项目目录 .env 读取
    _env_file = os.path.join(_BASE_DIR, ".env")
    if os.path.exists(_env_file):
        with open(_env_file, "r", encoding="utf-8") as _f:
            for _line in _f:
                if _line.strip().startswith("DEEPSEEK_API_KEY="):
                    DEEPSEEK_API_KEY = _line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY
                    break

if not DEEPSEEK_API_KEY:
    raise RuntimeError(
        "DEEPSEEK_API_KEY not found. Please either:\n"
        "  1. Set env var: set DEEPSEEK_API_KEY=sk-xxx\n"
        "  2. Or put key in C:\\Users\\24675\\Desktop\\API.txt\n"
        "  3. Or create .env file in project dir with DEEPSEEK_API_KEY=sk-xxx"
    )

# 设置到当前进程环境变量，方便后续使用
os.environ["DEEPSEEK_API_KEY"] = DEEPSEEK_API_KEY

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# ============================================================
# 加载品牌资料 & 爆款范例（从文件读取，作为 Prompt 上下文）
# ============================================================
def _load_file(path: str) -> str:
    """安全读取文件，文件不存在则返回空字符串"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

# 文件路径优先从项目目录读取，其次从桌面读取
import sys
_PRODUCTS_PATH = os.path.join(_BASE_DIR, "products.txt")
_EXAMPLES_PATH = os.path.join(_BASE_DIR, "examples.txt")

# 如果项目目录没有，尝试桌面
if not os.path.exists(_PRODUCTS_PATH):
    _PRODUCTS_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "products.txt")
if not os.path.exists(_EXAMPLES_PATH):
    _EXAMPLES_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "examples.txt")
    if not os.path.exists(_EXAMPLES_PATH):
        _EXAMPLES_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "examples.txt")

BRAND_INFO = _load_file(_PRODUCTS_PATH)
EXAMPLES = _load_file(_EXAMPLES_PATH)


# ============================================================
# 底层调用封装
# ============================================================
def _call_deepseek(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """
    调用 DeepSeek API，返回 AI 回复文本。
    统一异常处理：失败返回 "调用失败，请稍后再试"
    """
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        print(f"[AI 调用异常] {e}")
        return "调用失败，请稍后再试"


def _parse_json_safely(text: str, fallback: dict) -> dict:
    """
    安全解析 AI 返回的 JSON。
    返回解析后的字典；解析失败则返回 fallback。
    """
    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 尝试提取 ```json ... ``` 代码块
    if "```json" in text:
        try:
            start = text.index("```json") + 7
            end = text.index("```", start)
            return json.loads(text[start:end].strip())
        except (ValueError, json.JSONDecodeError):
            pass
    # 尝试提取第一个 { 到最后一个 }
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        pass
    # 兜底
    return fallback


# ============================================================
# 函数 1：调性审核（tone_check）
# ============================================================
def tone_check(script_content: str) -> dict:
    """
    审核达人脚本是否符合言仓品牌调性。

    输入：
        script_content (str): 达人写的小红书脚本正文
    输出：
        dict:
            - score:       0-100 分的调性匹配分
            - problems:    3 个具体的问题点（列表）
            - revised_script: 完整的润色后版本（字符串）
    """
    system_prompt = f"""你是一个严格的言仓文创品牌内容审核员。你的任务是对KOL脚本进行调性打分和润色。

# 品牌信息
{BRAND_INFO}

# 言仓爆款笔记参考（这才是"言仓味"的唯一标准）
{EXAMPLES}

# 审核标准
加分项（+分）：
- 有个人真实感受，用"我觉得""对我来说"等口语化表达
- 有情感共鸣，能引起读者共情
- 语气治愈、温暖、文艺，不焦虑
- 突出产品的情绪价值而非功能
- 突出生活仪式感和小确幸

减分项（-分）：
- 出现硬广词：闭眼入、冲、必买、绝绝子、YYDS、全网爆款、销量第一
- 太营销腔、太生硬、像产品说明书
- 说教语气："你应该""你必须"
- 没有个人体验，只罗列产品功能

# 输出要求
请严格按照以下 JSON 格式输出（不要输出任何其他内容）：
```json
{{
  "score": 数字(0-100),
  "problems": [
    "问题1的具体描述",
    "问题2的具体描述",
    "问题3的具体描述"
  ],
  "revised_script": "完整的润色后脚本（保留原意，注入言仓味）"
}}
```
"""

    user_prompt = f"""请审核以下达人脚本，并输出 JSON：

{script_content}"""

    ai_response = _call_deepseek(system_prompt, user_prompt, temperature=0.3)
    fallback = {
        "score": 0,
        "problems": ["API 返回异常，无法分析", "", ""],
        "revised_script": "调用失败，请稍后再试",
    }
    result = _parse_json_safely(ai_response, fallback)
    # 确保字段完整
    result.setdefault("score", 0)
    result.setdefault("problems", ["", "", ""])
    result.setdefault("revised_script", "调用失败，请稍后再试")
    return result


# ============================================================
# 函数 2：爆文拆解 & 套用（hot_note_break）
# ============================================================
def hot_note_break(note_content: str, product_name: str) -> dict:
    """
    拆解小红书爆文结构，套用指定产品生成新脚本。

    输入：
        note_content (str): 一篇小红书爆文的正文
        product_name (str): 要替换的目标产品名（任意品类）
    输出：
        dict:
            - structure: 原爆文的结构拆解（逐段分析原文内容+手法）
            - scripts:   3 篇套用该结构的新脚本（列表）
    """
    system_prompt = f"""你是一个小红书爆文拆解专家，专精于文创领域（文化创意产品）的内容分析。

你的核心能力是：识别一篇笔记用了什么"爆款公式"和"开头钩子类型"，逐段拆解其写作手法，然后用完全相同的结构为全新产品生成脚本。

# 言仓品牌信息（供理解温暖治愈的文案风格）
{BRAND_INFO}

# 言仓爆款笔记参考（这才是"言仓味"的唯一标准）
{EXAMPLES}

# 小红书爆款公式分类（你必须先识别原文属于哪一种）

1. 数字清单型
   特征：痛点 → 数字预告 → 分段清单 → 互动引导
   文创案例："打工人的5件桌面治愈好物，第3件直接封神"
   适用：好物合集、送礼清单、桌面搭配

2. 对比反差型
   特征：对比开场 → 分析差异 → 个人选择 → 情感升华
   文创案例："以前送朋友都是口红香水，今年换了言仓日历她哭了"
   适用：功能品vs情绪品、贵价vs用心、以前vs现在

3. 避坑指南型
   特征：警告开场 → 踩坑点+后果+正确做法 → 总结推荐
   文创案例："别再乱买日历了！选对一本能治愈你一整年"
   适用：品质科普、选购建议

4. 情绪共鸣型
   特征：情绪钩子 → 个人故事 → 产品出场 → 情感升华 → 松弛金句结尾
   文创案例："谁懂啊！这个线条小狗日历真的治愈了我的上班emo"
   适用：个人体验、治愈分享、情绪表达（**言仓最常用的类型**）

5. 揭秘内幕型
   特征：建立可信度 → 揭秘细节 → 实用建议
   文创案例："在文创行业待了3年，告诉你什么日历才值得买"
   适用：设计师故事、工艺科普、品牌理念

6. 教程步骤型
   特征：展示结果 → 步骤拆解 → 注意事项 → 效果对比
   文创案例："3步打造治愈系桌面，打工人用的小确幸"
   适用：桌面布置、开箱展示、使用教程

7. 资源合集型
   特征：价值承诺 → 分类整理 → 获取方式 → 收藏引导
   文创案例："2026年最值得收藏的文创日历清单，建议收藏"
   适用：送礼指南、品类合集

8. 身份召唤型
   特征：身份标签 → 专属共鸣 → 产品出场 → 圈层认同
   竞品案例：豆瓣"影迷必入！2026豆瓣电影日历把光影浪漫搬进日常"、九口山"爱书人必备！九口山读书笔记本太好用了"
   适用：特定圈层产品（书迷/影迷/手帐er/猫奴）、身份认同强的品类

9. 感官体验型
   特征：感官词开场 → 触觉/视觉细节描写 → 情绪反应 → 拥有欲望
   竞品案例：赛龙文具"救命！这个毛绒笔记本也太好rua了吧"、唔哟"软fufu的，抱着就不想撒手"
   适用：材质突出、触感特别的产品（毛绒、纸质、布艺）

# 小红书开头钩子分类（识别原文第一句话属于哪种）

1. 呈现结果型：直接把最好的结果/画面展示出来 → "被问了800遍的书桌，终于整理好了"
2. 罗列痛点型：一口气说出目标人群的所有困扰 → "上班打瞌睡、心情容易崩、桌面乱成狗窝"
3. 引起恐慌型：制造紧迫感或损失感 → "错过这波联名，下次又要等一年"
4. 提问型：用问题勾起好奇心 → "你们收到过最有意义的礼物是什么？"
5. 讲故事型：用一个小故事或场景自然引入 → "给闺蜜送了这个坏心情急救包，她抱着我说你怎么这么懂我"
6. 场景呈现型：描绘一个具体生动的日常场景 → "早上7点闹钟响了，翻开日历看到小狗在说'今天也要开心'"
7. 反常识型：说一个和常规认知相反的观点 → "最好的礼物从来都不是最贵的，而是最用心的"
8. 制造冲突型：用一个矛盾或对比引发好奇 → "月薪3千花69买日历，我妈说我疯了，但我觉得太值了"
9. 直入正题型：直接开始说产品，不加铺垫 → "线条小狗控狂喜！言仓联名终于来了"
10. 身份召唤型：用身份标签喊出目标人群 → "手帐党集合！🫡"、"影迷必入！"、"爱书人必备！"
11. 绝版紧迫型：制造稀缺感或时代终结感 → "2026年，是单向历纸质版的最后一年"、"最后一本纸质版，再见了我的青春"

# 治愈系文创文案技法（言仓味的核心DNA，生成脚本时必须融入至少2种）

1. 产品人格化：把产品当作有生命、有性格的朋友来写
   不写"日历设计得很好"，写"今天的小狗举着奶茶对我说'今天也要开心'"
   文创产品不是工具，是陪伴者

2. 微小时刻（micro-moments）：捕捉日常中极易被忽略的温暖瞬间
   "每天早上翻一页日历"、"撕下的纸舍不得扔当书签"、"同事路过笑着问这是什么"
   不说大道理，只说小细节

3. 留白与松弛：不填满每一句，留有诗意间隙
   短句比长句更有力量：用完一个长段后，用一句短句收住
   段落末尾留一句轻盈的话，像叹气一样自然

4. 松弛金句：不说教不鸡汤，像朋友随口说的一句话
   "生活已经够苦了，总要给自己找点甜"
   "身体不能远行，灵魂先在路上"
   "世界破破烂烂，小狗缝缝补补"

5. 情绪价值优先：永远先说"它让你感觉怎么样"，再说"它是什么"
   不写"这款日历有365页手绘小狗"
   写"每天翻开都能看到不同的小狗表情，抬头看到就觉得心情变好了"

6. 触觉语言（感官唤醒）：用触感词汇让读者"云触摸"产品，制造拥有的冲动
   竞品示范：赛龙"软fufu的毛绒材质，摸起来就像rua小猫咪"、唔哟"抱着它就像被全世界温柔地抱着"
   言仓化："纸质的触感好到舍不得撕"、"翻开的那一瞬间，纸张的厚度让你觉得每一天都值得认真过"

7. 情感存档（记忆容器）：把产品定位为记忆的载体、时光的容器，而非功能品
   竞品示范：青禾纪"手工相册的意义，不是多精致，而是让对方知道，和他有关的每一件小事，你都偷偷珍藏着"、豆瓣"它不像普通日历只标记日子，更像一本藏着万千故事的光影手账"
   言仓化："撕下的每一页不是废纸，是那一天活过的证据"

8. 知识浪漫主义：用文化/艺术/哲学视角赋予产品精神深度，让读者觉得"买它是有品味的"
   竞品示范：单向空间"许知远的精神自留地"、"在这个慌张的时代，做一个不慌的人"、青禾纪"允许自己浪漫得毫无道理，愿你在任何秩序里，都能长出自己野生的韵脚"
   言仓化：不说"这个日历很好看"，说"每天一句来自远方的问候，提醒你生活还有诗意"

# 禁忌清单（生成脚本时严格遵守）

- 禁止硬广词：闭眼入、冲、必买、绝绝子、YYDS、全网爆款、销量第一、赶紧买、链接放主页
- 禁止说教语气：你必须、你应该、不买就亏了、错过后悔
- 禁止功能罗列：只说参数和规格，没有真实感受
- 禁止虚假故事：编造不真实的情感描述

# 你的任务（两步，必须严格按顺序执行）

## 第一步：拆解原文结构

请逐段阅读用户提供的笔记，输出以下内容：

1. 【公式分类】这篇笔记整体属于哪种爆款公式？（从上面9种中选最匹配的1种）
2. 【钩子分类】原文的开头属于哪种钩子类型？（从上面11种中选1种）
3. 【逐段拆解】对原文的每一段：
   - label: 这段在原文中起什么作用？用具体的技法名称，如"场景式开场""产品人格化描写""个人体验叙述""松弛金句收尾"。不要笼统写"正文1""正文2"。
   - quote: 必须引用原文中真实存在的具体句子（至少15个字），禁止概括或编造
   - analysis: 分析这段写了什么 + 用了什么写作手法（需命名具体技法）+ 在整篇结构中的承上启下作用 + 读者看完的感受

重要约束：
- 段数由原文决定，原文有几段就拆几段，不强行套模板
- quote字段必须是原文真实存在的句子，如果找不到对应原文就说明这段不存在
- analysis中必须命名具体技法，至少包含一种上面提到的"治愈系文创技法"或"爆款公式特征"

## 第二步：套用结构生成3篇新脚本

目标产品：【{product_name}】

基于第一步拆出的原文真实结构，写3篇全新的小红书种草笔记：

生成要求：
- 每篇脚本的段落数量和节奏必须与原文完全相同
- 把产品换成【{product_name}】，但情感推进逻辑不变
- 3篇脚本必须分别使用不同的开头钩子类型（从11种中选3种，且3种必须互不相同）
- 每篇至少融入2种治愈系文创技法
- 3篇脚本分别从不同角度切入：自用感受 / 送礼场景 / 日常陪伴
- 用第一人称，有真实个人感受
- 严格遵守禁忌清单

# 输出范例（以下是一个标准拆解+生成的示范，请严格参照这个深度和质量）

假设输入是一篇青禾纪的爆文笔记：
"mini相册本闪亮登场啦！一翻开就感觉陷入了回忆的海洋🌊 既能收纳 mini 拍立得照片，也能写下拍摄心情与日常记录，就像做了一本mini zine！一物俩用get！还能出门旅行携带～ 颜值也很抗打，美丽小本子很难不心动～ 这种小物品简直是提升幸福感的好物 给零散的回忆安一个小小的家🏠"

正确输出应该是：

```json
{{
  "formula": "感官体验型",
  "hook_type": "直入正题型",
  "structure": {{
    "segments": [
      {{
        "label": "产品登场+感官冲击",
        "quote": "mini相册本闪亮登场啦！一翻开就感觉陷入了回忆的海洋🌊",
        "analysis": "用'闪亮登场'制造新品发布的仪式感，紧接着用'陷入回忆的海洋'这个比喻将物理动作（翻页）转化为情感体验（沉浸回忆），这是'情感存档'技法的典型应用——产品=记忆容器。读者看到这句话会下意识联想到自己的珍贵照片，产生情感共鸣。"
      }},
      {{
        "label": "功能场景化描写",
        "quote": "既能收纳 mini 拍立得照片，也能写下拍摄心情与日常记录，就像做了一本mini zine！",
        "analysis": "没有干巴巴列参数，而是把功能融入使用场景：'收纳照片+写心情+做zine'三合一。用'mini zine'这个手帐圈术语精准击中目标人群（身份召唤），让读者觉得'这就是我要的'。触觉语言藏在'收纳''写下'这些动作词里。"
      }},
      {{
        "label": "便携性+颜值双重种草",
        "quote": "一物俩用get！还能出门旅行携带～ 颜值也很抗打，美丽小本子很难不心动～",
        "analysis": "'一物俩用'是性价比暗示，'出门旅行携带'拓展了使用场景（不只是在家用）。'颜值抗打'用年轻化口语降低距离感，'很难不心动'制造从众心理。这是典型的'情绪价值优先'——先说它能陪你旅行，再说它好看。"
      }},
      {{
        "label": "松弛金句收尾",
        "quote": "这种小物品简直是提升幸福感的好物 给零散的回忆安一个小小的家🏠",
        "analysis": "先用'提升幸福感'完成价值升华（不说'很实用'而说'很幸福'），最后用'给零散的回忆安一个小小的家'收尾——这是'情感存档'技法的高阶用法，把产品比喻成'家'，让读者产生温暖归属感。短句收束，留白有余韵。"
      }}
    ]
  }},
  "scripts": [
    "📸 终于给我的拍立得找到了完美小家！\n\n之前拍了一堆mini拍立得全塞在抽屉里，翻出来的时候发现好多都粘在一起了😭。这个相册本简直救了命，一翻开就能看到所有回忆整整齐齐地躺在里面，那种满足感谁懂啊！\n\n每张照片旁边还能随手写几句当时的心情，翻着翻着就笑了。原来二月的那天我写了'今天吃的火锅巨好吃'，四月的拍立得旁边画了一只丑丑的猫。\n\n现在出门旅行必带它，白天拍照晚上贴，像在做一本属于自己的旅行杂志。朋友翻到的时候尖叫说'这太可爱了吧你什么时候偷偷搞的'。\n\n给那些散落在各处的回忆，安一个可以随时翻开的家吧。",

    "🎁 给闺蜜准备了一份'年度回忆册'\n\n从我们认识那年到现在，我把所有合照都翻出来贴进去了。有些照片已经泛黄了，但贴在这个本子上的时候，好像那些日子又活过来了。\n\n不只是照片——电影票根、火车票、她写给我的小纸条，全都找到了归属。每翻一页都是我们一起走过的路。那些聊天记录会沉底，但这个本子她会一直翻。\n\n最戳我的是，我在最后一页写了一句'谢谢你成为我生命中特别的存在'。她收到的时候当着我的面哭了三分钟。\n\n最用心的礼物从来不需要多贵，只需要让对方知道：和你有关的每一件小事，我都珍藏着。",

    "🍃 每天花5分钟，积攒了一整年的幸福\n\n睡前放下手机，花五分钟翻翻今天的照片，挑一张最喜欢的贴在本子上，在旁边写一句今天发生的小事。\n\n坚持了三个月后往回翻，才发现原来我的生活里有这么多值得记住的瞬间：三月窗外的樱花开了、五月楼下猫咪生了一窝崽、七月暴雨天在家煮了一碗超成功的泡面。\n\n这些小事放在日常里根本不会在意，但被这个本子收着的时候，你会觉得'原来我过得还挺有意思的'。\n\n它就像一个不会说话的朋友，安静地替你保管着那些容易被遗忘的快乐。给零散的日常，安一个小小的家吧。"
  ]
}}
```

请注意这个范例的几个关键特征（你输出的每一条都必须达到这个标准）：
- 每段都引用了原文真实句子（quote ≥15字）
- 每段analysis都命名了具体技法（情感存档、身份召唤、触觉语言、情绪价值优先、松弛金句）
- 技法名称必须从上面列出的8种治愈技法或9种爆款公式特征中选取
- 3篇脚本用了3种不同的钩子（呈现结果型/讲故事型/场景呈现型），角度各不相同
- 每篇脚本都融入了至少2种治愈技法，且严格遵守禁忌清单

# 输出格式

严格按照以下 JSON 输出（不要输出任何其他内容）：
```json
{{
  "formula": "原文使用的爆款公式名称",
  "hook_type": "原文使用的钩子类型名称",
  "structure": {{
    "segments": [
      {{
        "label": "这段的作用（需体现技法名称）",
        "quote": "引用的原文原句（至少15字，禁止编造）",
        "analysis": "手法分析：写了什么 + 用了什么技法 + 结构作用 + 读者感受"
      }}
    ]
  }},
  "scripts": [
    "第1篇完整脚本（钩子类型A，自用感受角度）",
    "第2篇完整脚本（钩子类型B，送礼场景角度）",
    "第3篇完整脚本（钩子类型C，日常陪伴角度）"
  ]
}}
```
"""

    user_prompt = f"""目标产品：{product_name}

请先识别下面笔记的爆款公式和钩子类型，再逐句拆解其真实结构（必须引用原文），然后生成3篇套用该结构的全新脚本：

---
{note_content}
---"""

    ai_response = _call_deepseek(system_prompt, user_prompt, temperature=0.8)
    fallback = {
        "formula": "未能识别",
        "hook_type": "未能识别",
        "structure": {"segments": []},
        "scripts": ["调用失败，请稍后再试", "", ""],
    }
    result = _parse_json_safely(ai_response, fallback)
    result.setdefault("formula", "未能识别")
    result.setdefault("hook_type", "未能识别")
    result.setdefault("structure", {"segments": []})
    result.setdefault("scripts", ["调用失败，请稍后再试", "", ""])
    return result


# ============================================================
# 函数 3：评论分析（comment_analysis）
# ============================================================
def comment_analysis(comments_list: list) -> dict:
    """
    分析小红书笔记评论，得出用户反馈和优化建议。

    输入：
        comments_list (list): 每条评论为一个字符串
    输出：
        dict:
            - top_keywords:      高频词 TOP10（列表，每个为 {{"word": "xxx", "count": 10}}）
            - emotion_ratio:     情绪占比（positive / neutral / negative 的百分比）
            - top_selling_points: 用户最关注的 3 个卖点（列表）
            - suggestion:        100 字以内的优化建议（字符串）
    """
    # 将评论拼接成带编号的文本
    comments_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(comments_list)])

    system_prompt = """你是一个小红书数据分析专家，专门分析笔记评论区的用户反馈。

# 你的任务
分析以下评论列表，输出结构化结论。

# 分析维度
1. 高频词 TOP10：提取评论中出现频率最高的10个有意义的词（排除"的""了""我""是"等停用词），统计出现次数
2. 情绪占比：判断每条评论的情感倾向（正面/中性/负面），给出百分比（三项之和=100%）
3. 用户最关注的3个卖点：从评论中提炼用户最在意的产品卖点
4. 优化建议：基于评论反馈，给出100字以内的内容优化建议

# 输出要求
严格按照 JSON 格式输出：
```json
{
  "top_keywords": [
    {"word": "关键词1", "count": 数字},
    ...
  ],
  "emotion_ratio": {
    "positive": 数字(百分比),
    "neutral": 数字(百分比),
    "negative": 数字(百分比)
  },
  "top_selling_points": [
    "卖点1",
    "卖点2",
    "卖点3"
  ],
  "suggestion": "100字以内的优化建议"
}
```"""

    user_prompt = f"请分析以下评论列表：\n\n{comments_text}"

    ai_response = _call_deepseek(system_prompt, user_prompt, temperature=0.3)
    fallback = {
        "top_keywords": [],
        "emotion_ratio": {"positive": 0, "neutral": 0, "negative": 0},
        "top_selling_points": [],
        "suggestion": "调用失败，请稍后再试",
    }
    result = _parse_json_safely(ai_response, fallback)
    result.setdefault("top_keywords", [])
    result.setdefault("emotion_ratio", {"positive": 0, "neutral": 0, "negative": 0})
    result.setdefault("top_selling_points", [])
    result.setdefault("suggestion", "调用失败，请稍后再试")
    return result


# ============================================================
# 模块自测（直接运行此文件时执行）
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("[TEST] ai_tools.py Self-Test")
    print("=" * 60)

    # --- Test 1: tone_check ---
    print("\n[TEST 1/3] tone_check (Brand Tone Audit)")
    test_script = """啊啊啊姐妹们这个线条小狗日历也太可爱了吧！
必入！闭眼入！每一个都好好看，放在桌上心情都会变好。
69块钱又不贵，冲冲冲！言仓真的YYDS！"""
    result1 = tone_check(test_script)
    print(f"   Score: {result1.get('score')}")
    print(f"   Problems: {result1.get('problems')[:2]}...")
    print(f"   Revised preview: {result1.get('revised_script', '')[:80]}...")
    ok1 = result1.get("score", 0) != 0 or "失败" not in str(result1.get("problems", ""))
    print(f"   {'[OK] tone_check success' if ok1 else '[WARN] Result may be invalid'}")

    # --- Test 2: hot_note_break ---
    print("\n[TEST 2/3] hot_note_break (Viral Note Breakdown)")
    test_note = """谁懂啊！！这个杯子真的长在我心巴上了
每天早上用它喝水都觉得自己是精致girl
而且才39块钱，质量超好，用了半年都没掉色
链接放主页了，姐妹们自取～"""
    result2 = hot_note_break(test_note, "坏心情急救包")
    formula = result2.get('formula', '?')
    hook_type = result2.get('hook_type', '?')
    print(f"   Formula: {formula}")
    print(f"   Hook Type: {hook_type}")
    structure = result2.get('structure', {})
    segments = structure.get('segments', [])
    print(f"   Structure segments: {len(segments)}")
    for seg in segments[:2]:
        print(f"     [{seg.get('label','?')}] quote: {seg.get('quote','')[:50]}...")
        print(f"     analysis: {seg.get('analysis','')[:80]}...")
    scripts = result2.get('scripts', [])
    print(f"   Scripts generated: {len(scripts)}")
    if scripts and scripts[0] != "调用失败，请稍后再试":
        print(f"   Script 1 preview: {scripts[0][:80]}...")
    ok2 = len(scripts) == 3
    print(f"   {'[OK] hot_note_break success' if ok2 else '[WARN] Result may be invalid'}")

    # --- Test 3: comment_analysis ---
    print("\n[TEST 3/3] comment_analysis (Comment Analysis)")
    test_comments = [
        "小狗日历太治愈了！每天上班看到它心情都变好",
        "买来送闺蜜的，她收到哭了说太懂她了",
        "会掉色吗？有点担心质量",
        "已经收到啦！包装超用心，还有手写卡片，感动",
        "说实话有点贵，59还可以接受",
        "求链接！！这个小狗音箱在哪里买",
        "这个日历纸质好差，撕的时候很失望",
        "太可爱了叭！言仓的东西从来不会让人失望",
        "买了三个送人，大家都说好喜欢",
        "一般般吧，就是普通日历的样子",
    ]
    result3 = comment_analysis(test_comments)
    print(f"   Keywords: {result3.get('top_keywords', [])[:3]}...")
    print(f"   Emotion: {result3.get('emotion_ratio')}")
    print(f"   Selling points: {result3.get('top_selling_points')}")
    print(f"   Suggestion: {result3.get('suggestion', '')[:60]}...")
    ok3 = bool(result3.get("top_keywords"))
    print(f"   {'[OK] comment_analysis success' if ok3 else '[WARN] Result may be invalid'}")

    print("\n" + "=" * 60)
    print("[DONE] Self-test complete!")
