"""
app.py --- Streamlit Frontend
言仓文创 KOL 专属内容品控 & 复盘工作台
设计语言：拓竹 Bambu Lab 式极简高级感 × 言仓温暖治愈调性
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import base64

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_tools import tone_check, hot_note_break

# ============================================================
# 加载轮播图片 → base64（不依赖外部服务，自包含）
# ============================================================
def _load_image_b64(filename):
    """读取 static/ 下图片，返回 base64 data URI"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", filename)
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{data}"

IMG1 = _load_image_b64("slide1.jpg")
IMG2 = _load_image_b64("slide2.jpg")
IMG3 = _load_image_b64("slide3.jpg")

# 产品图（atmosphere zone + 产品展示条）
import glob as _glob
_prod_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "products")
_PROD_IMGS = []
for _f in sorted(_glob.glob(os.path.join(_prod_dir, "*.jpg"))):
    with open(_f, "rb") as _fh:
        _PROD_IMGS.append(f"data:image/jpeg;base64,{base64.b64encode(_fh.read()).decode('utf-8')}")

# 日历图（底部日历专区）
_cal_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "calendar")
CAL_IMGS = []
for _f in sorted(_glob.glob(os.path.join(_cal_dir, "*.jpg"))):
    with open(_f, "rb") as _fh:
        CAL_IMGS.append(f"data:image/jpeg;base64,{base64.b64encode(_fh.read()).decode('utf-8')}")

# ============================================================
# Page config
# ============================================================
st.set_page_config(
    page_title="言仓文创 | KOL内容品控",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get help': None,
        'Report a bug': None,
        'About': None,
    },
)

# 拦截 Streamlit 开发者快捷键（防止误触 C 键弹 Clear Cache）
st.markdown("""
<script>
(function() {
    var blockKeys = ['c', 'C'];
    window.addEventListener('keydown', function(e) {
        var tag = document.activeElement ? document.activeElement.tagName : '';
        var isInput = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || document.activeElement.isContentEditable;
        if (!isInput && !e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey && blockKeys.includes(e.key)) {
            e.preventDefault();
            e.stopPropagation();
        }
    }, {capture: true});
})();
</script>
""", unsafe_allow_html=True)

# ============================================================
# CSS — 拓竹式极简设计 + 言仓暖调
# ============================================================
_css = """
<style>
    /* ========== 全局 ========== */
    .stApp {
        background: #faf7f2;
    }

    /* 字体只作用于可见文本元素，避免污染 Streamlit 内部隐藏节点 */
    body, p, h1, h2, h3, h4, h5, h6, div, span,
    button, input, textarea, select, label, a,
    li, td, th, blockquote, pre, code, caption {
        font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
    }

    /* ========== 顶部导航栏 ========== */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 2rem;
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    .top-nav .logo {
        font-size: 1.1rem;
        font-weight: 700;
        color: #3d3226;
        letter-spacing: 0.03em;
    }
    .top-nav .logo span {
        color: #c47f4a;
        font-weight: 400;
        font-size: 0.82rem;
        margin-left: 0.5rem;
    }
    .top-nav .badge {
        font-size: 0.74rem;
        color: #8b7e6a;
        background: #f5f0e8;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
    }

    /* ========== Hero 区 ========== */
    .hero {
        text-align: center;
        padding: 1.5rem 0 2rem;
    }
    .hero h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #3d3226;
        letter-spacing: 0.04em;
        margin-bottom: 0.4rem;
    }
    .hero .desc {
        font-size: 0.9rem;
        color: #8b7e6a;
        font-weight: 400;
    }
    .hero .slogan {
        font-size: 0.78rem;
        color: #b8a894;
        margin-top: 0.3rem;
    }

    /* ========== 指标卡片 ========== */
    .stat-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.8rem;
    }
    .stat-card {
        flex: 1;
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.04);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        text-align: center;
        transition: box-shadow 0.25s, transform 0.25s;
    }
    .stat-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        transform: translateY(-1px);
    }
    .stat-card .label {
        font-size: 0.76rem;
        color: #8b7e6a;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.4rem;
    }
    .stat-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3d3226;
    }
    .stat-card .sub {
        font-size: 0.74rem;
        color: #b8a894;
        margin-top: 0.2rem;
    }

    /* ========== 主内容卡片 ========== */
    .content-card {
        background: #ffffff;
        border: 1px solid rgba(0,0,0,0.04);
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.2rem;
    }
    .content-card .card-title,
    .card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #3d3226;
        margin-bottom: 0.3rem;
    }
    .content-card .card-desc,
    .card-desc {
        font-size: 0.8rem;
        color: #6b5e4a;
        margin-bottom: 1rem;
    }

    /* ========== 分数胶囊 ========== */
    .score-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        border-radius: 50%;
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-right: 1rem;
    }
    .score-high { background: linear-gradient(135deg, #7a9e7a, #6b8e6b); }
    .score-mid  { background: linear-gradient(135deg, #c4a24a, #b8923a); }
    .score-low  { background: linear-gradient(135deg, #c47a6a, #b86a5a); }

    /* ========== 问题项 ========== */
    .problem-item {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.6rem 0.9rem;
        margin: 0.35rem 0;
        background: #fdfaf5;
        border-radius: 8px;
        font-size: 0.84rem;
        color: #5a4a3a;
        border: 1px solid rgba(0,0,0,0.03);
    }
    .problem-item .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #c4a24a;
        margin-top: 0.5rem;
        flex-shrink: 0;
    }

    /* ========== 脚本卡片 ========== */
    .script-card {
        background: #fdfaf5;
        border: 1px solid rgba(0,0,0,0.04);
        border-radius: 10px;
        padding: 1rem 1.3rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        line-height: 1.85;
        color: #3d3226;
    }

    /* ========== 按钮 ========== */
    .stButton > button {
        background: #3d3226 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.8rem !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em;
        transition: all 0.25s !important;
    }
    .stButton > button:hover {
        background: #c47f4a !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(196,127,74,0.3);
    }

    /* ========== Select / Slider / Radio ========== */
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
    }
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        background: #fdfcf9 !important;
        color: #3d3226 !important;
    }
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: #b8a894 !important;
        opacity: 1 !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #c47f4a !important;
        box-shadow: 0 0 0 2px rgba(196,127,74,0.12) !important;
    }

    /* ========== Expander ========== */
    .stExpander {
        border: 1px solid rgba(0,0,0,0.04) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    .stExpander summary {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* ========== 底部 ========== */
    .app-footer {
        text-align: center;
        color: #b8a894;
        font-size: 0.74rem;
        padding: 1.8rem 0 0.8rem;
    }

    /* ========== 空状态引导 ========== */
    .empty-guide {
        text-align: center;
        padding: 2.5rem 1rem;
        color: #b8a894;
    }
    .empty-guide .icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
    }
    .empty-guide .title {
        font-size: 1rem;
        font-weight: 600;
        color: #8b7e6a;
        margin-bottom: 0.5rem;
    }
    .empty-guide p {
        font-size: 0.82rem;
        line-height: 1.8;
        margin: 0;
    }

    /* ========== 分割线 ========== */
    .divider {
        height: 1px;
        background: rgba(0,0,0,0.04);
        margin: 1rem 0;
    }

    /* ================================================================
       Kill Streamlit loading chrome — 拓竹式纯净体验，零干扰
       ================================================================ */
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
        height: 0 !important;
        position: fixed !important;
    }
    #MainMenu { visibility: hidden !important; height: 0 !important; }
    header[data-testid="stHeader"] { visibility: hidden !important; height: 0 !important; }
    footer { visibility: hidden !important; height: 0 !important; }
    /* 隐藏开发者对话框（Clear Cache 等） */
    div[data-baseweb="modal"] { display: none !important; }
    div[data-baseweb="drawer"] { display: none !important; }

    /* ================================================================
       定制加载动画 — 言仓暖调旋转环
       ================================================================ */
    @keyframes spinRing {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes pulseText {
        0%, 100% { opacity: 0.6; }
        50%      { opacity: 1; }
    }
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2.5rem 1rem;
        gap: 1rem;
    }
    .loading-ring {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 3px solid #f0ebe3;
        border-top-color: #c47f4a;
        animation: spinRing 0.8s linear infinite;
    }
    .loading-text {
        font-size: 0.82rem;
        color: #8b7e6a;
        font-weight: 500;
        animation: pulseText 1.6s ease-in-out infinite;
        letter-spacing: 0.03em;
    }

    /* ================================================================
       Hero 图片轮播 — 纯 CSS 3 张图淡入淡出，致敬拓竹首屏
       ================================================================ */
    @keyframes carouselFade1 {
        0%, 28%  { opacity: 1; }
        33%, 95% { opacity: 0; }
        100%     { opacity: 1; }
    }
    @keyframes carouselFade2 {
        0%, 28%  { opacity: 0; }
        33%, 61% { opacity: 1; }
        66%, 100% { opacity: 0; }
    }
    @keyframes carouselFade3 {
        0%, 61%  { opacity: 0; }
        66%, 95% { opacity: 1; }
        100%     { opacity: 0; }
    }
    @keyframes carouselZoom {
        0%, 100% { transform: scale(1); }
        50%      { transform: scale(1.06); }
    }
    .hero-carousel {
        position: relative;
        width: 100%;
        max-width: 960px;
        height: 420px;
        overflow: hidden;
        border-radius: 16px;
        margin: 0 auto 1.2rem;
    }
    .hero-carousel .slide {
        position: absolute;
        inset: 0;
        background-size: cover;
        background-position: center;
        opacity: 0;
        animation: carouselZoom 18s ease-in-out infinite;
    }
    .hero-carousel .slide:nth-child(1) {
        background: url('__IMG1__') center/cover no-repeat;
        animation-name: carouselFade1, carouselZoom;
    }
    .hero-carousel .slide:nth-child(2) {
        background: url('__IMG2__') center/cover no-repeat;
        animation-name: carouselFade2, carouselZoom;
    }
    .hero-carousel .slide:nth-child(3) {
        background: url('__IMG3__') center/cover no-repeat;
        animation-name: carouselFade3, carouselZoom;
    }
    /* 每张 slide 上的暗色遮罩 */
    .hero-carousel .slide::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(61,50,38,0.15) 0%, rgba(61,50,38,0.35) 100%);
    }
    .hero-carousel .carousel-overlay {
        position: absolute;
        inset: 0;
        z-index: 2;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        pointer-events: none;
    }
    .hero-carousel .carousel-overlay h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 12px rgba(0,0,0,0.25);
    }
    .hero-carousel .carousel-overlay .desc {
        font-size: 0.92rem;
        color: rgba(255,255,255,0.88);
        font-weight: 400;
        text-shadow: 0 1px 6px rgba(0,0,0,0.2);
    }
    .hero-carousel .carousel-overlay .slogan {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.7);
        margin-top: 0.5rem;
        text-shadow: 0 1px 4px rgba(0,0,0,0.18);
    }

    /* ================================================================
       深色品牌理念横幅 — 打破纯白单调，拓竹式深色对比区块
       ================================================================ */
    .brand-banner {
        max-width: 960px;
        margin: 0 auto 1.8rem;
        background: linear-gradient(135deg, #3d3226 0%, #4a3d2e 50%, #3d3226 100%);
        border-radius: 14px;
        padding: 2rem 2.5rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .brand-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(196,127,74,0.12) 0%, transparent 60%);
        animation: bannerGlow 8s ease-in-out infinite;
    }
    @keyframes bannerGlow {
        0%, 100% { transform: translate(0, 0); }
        50%      { transform: translate(2%, 1%); }
    }
    .brand-banner .banner-quote {
        position: relative;
        z-index: 1;
        font-size: 1.15rem;
        font-weight: 600;
        color: #e8d5c4;
        letter-spacing: 0.05em;
        line-height: 1.8;
    }
    .brand-banner .banner-sub {
        position: relative;
        z-index: 1;
        font-size: 0.8rem;
        color: rgba(232,213,196,0.55);
        margin-top: 0.6rem;
    }

    /* ================================================================
       产品氛围区 — 慢速 zoom 模拟视频呼吸感
       ================================================================ */
    @keyframes slowZoom {
        0%, 100% { transform: scale(1); }
        50%      { transform: scale(1.08); }
    }
    .atmosphere-zone {
        width: 100%;
        max-width: 960px;
        height: 280px;
        border-radius: 14px;
        overflow: hidden;
        margin: 0 auto 1.8rem;
        position: relative;
        background: linear-gradient(135deg, #e8ddd0, #d5c8b6, #c7b8a0, #d9cdb8);
    }
    .atmosphere-zone .atmo-bg {
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, #efe5d8 0%, #dccdb8 40%, #c9b595 70%, #e0d0b8 100%);
        animation: slowZoom 10s ease-in-out infinite;
    }
    .atmosphere-zone .atmo-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(61,50,38,0.08) 0%, rgba(61,50,38,0.25) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .atmosphere-zone .atmo-text {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.85);
        font-weight: 500;
        letter-spacing: 0.06em;
        text-shadow: 0 1px 8px rgba(0,0,0,0.2);
    }

    /* ================================================================
       滚动渐现动画 — 拓竹式内容逐块 reveal
       ================================================================ */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(24px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .reveal {
        animation: fadeInUp 0.7s ease-out both;
    }
    .reveal:nth-child(1) { animation-delay: 0.05s; }
    .reveal:nth-child(2) { animation-delay: 0.15s; }
    .reveal:nth-child(3) { animation-delay: 0.25s; }
    .reveal:nth-child(4) { animation-delay: 0.35s; }
    /* 兼容不支持 animation-timeline 的浏览器 — 直接播放 */
    @supports (animation-timeline: view()) {
        .reveal-scroll {
            animation: fadeInUp 0.7s ease-out both;
            animation-timeline: view();
            animation-range: entry 0% entry 85%;
        }
    }

    /* ================================================================
       卡片 hover 增强 — 更深的上浮 + 更明显的阴影
       ================================================================ */
    .stat-card {
        transition: box-shadow 0.3s ease, transform 0.3s ease !important;
    }
    .stat-card:hover {
        box-shadow: 0 8px 32px rgba(0,0,0,0.10) !important;
        transform: translateY(-4px) !important;
    }
    .content-card {
        transition: box-shadow 0.3s ease, transform 0.3s ease !important;
    }
    .content-card:hover {
        box-shadow: 0 6px 24px rgba(0,0,0,0.08) !important;
        transform: translateY(-2px) !important;
    }

    /* ================================================================
       Tab 样式修复 — 未选中态文字可见
       ================================================================ */
    button[data-baseweb="tab"] {
        color: #5a4a3a !important;
        font-weight: 500 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #3d3226 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #c47f4a !important;
    }

    /* ================================================================
       导航栏底部微阴影
       ================================================================ */
    .top-nav {
        box-shadow: 0 1px 0 rgba(0,0,0,0.03), 0 4px 16px rgba(0,0,0,0.03);
    }

    /* ================================================================
       产品展示条 — 横向可滚动卡片
       ================================================================ */
    .product-strip {
        max-width: 960px;
        margin: 0 auto 1.8rem;
    }
    .strip-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #3d3226;
        margin-bottom: 0.8rem;
        letter-spacing: 0.03em;
    }
    .prod-card-row {
        display: flex;
        gap: 0.8rem;
        overflow-x: auto;
        padding-bottom: 0.5rem;
        scrollbar-width: thin;
        scrollbar-color: #d4c4b0 transparent;
    }
    .prod-card-row::-webkit-scrollbar { height: 4px; }
    .prod-card-row::-webkit-scrollbar-thumb { background: #d4c4b0; border-radius: 4px; }
    .prod-card {
        flex: 0 0 200px;
        height: 240px;
        border-radius: 12px;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .prod-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 28px rgba(0,0,0,0.12);
    }
    .prod-card-img {
        width: 100%;
        height: 100%;
    }

    /* ================================================================
       日历专区 — 底部网格展示
       ================================================================ */
    .calendar-section {
        max-width: 960px;
        margin: 2rem auto 1.5rem;
    }
    .calendar-section .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #3d3226;
        letter-spacing: 0.03em;
        margin-bottom: 0.3rem;
    }
    .calendar-section .section-sub {
        font-size: 0.8rem;
        color: #8b7e6a;
        margin-bottom: 1rem;
    }
    .cal-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
    }
    .cal-card {
        border-radius: 12px;
        overflow: hidden;
        aspect-ratio: 3/4;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .cal-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 28px rgba(0,0,0,0.12);
    }
    @media (max-width: 768px) {
        .cal-grid { grid-template-columns: repeat(2, 1fr); }
    }
</style>
"""
_css = _css.replace("__IMG1__", IMG1).replace("__IMG2__", IMG2).replace("__IMG3__", IMG3)
st.markdown(_css, unsafe_allow_html=True)

# ============================================================
# 顶部导航
# ============================================================
st.markdown("""
<div class="top-nav">
    <div class="logo">言仓文创 <span>YANCANG</span></div>
    <div class="badge">KOL 内容品控</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# Hero — CSS 图片轮播（拓竹式首屏大图自动切换）
# 图片使用暖色渐变模拟言仓产品氛围，可替换为实际产品图 URL
# ============================================================
st.markdown("""
<div class="hero-carousel">
    <div class="slide"></div>
    <div class="slide"></div>
    <div class="slide"></div>
    <div class="carousel-overlay">
        <h1>让每一篇内容都有言仓味</h1>
        <p class="desc">品牌调性审核 &nbsp;·&nbsp; 爆文结构拆解</p>
        <p class="slogan">生命不慌张 —— 只做有温度的内容</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 深色品牌理念横幅 — 拓竹式深色对比区块
# ============================================================
st.markdown("""
<div class="brand-banner reveal">
    <p class="banner-quote">好的文创从不贩卖焦虑<br>它只是在你不经意翻开的瞬间，轻轻说了句"我懂你"</p>
    <p class="banner-sub">YANCANG &nbsp;·&nbsp; 为每一个微小时刻设计</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 产品氛围区 — 慢速 zoom 模拟视频呼吸感
# ============================================================
_atmo_img = _PROD_IMGS[4] if len(_PROD_IMGS) > 4 else _PROD_IMGS[0]
st.markdown(f"""
<div class="atmosphere-zone reveal">
    <div class="atmo-bg" style="background: url('{_atmo_img}') center/cover no-repeat;"></div>
    <div class="atmo-overlay">
        <span class="atmo-text">📦 线条小狗日历 · 坏心情急救包 · 旅行日历 · 小刘鸭联名</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 产品展示条 — 横向滚动展示言仓产品实拍
# ============================================================
_showcase_imgs = _PROD_IMGS[:6] if len(_PROD_IMGS) >= 6 else _PROD_IMGS
_cards_html = ""
for _i, _img in enumerate(_showcase_imgs):
    _cards_html += f'<div class="prod-card"><div class="prod-card-img" style="background: url(\'{_img}\') center/cover no-repeat;"></div></div>'
st.markdown(f"""
<div class="product-strip reveal">
    <p class="strip-label">产品图库</p>
    <div class="prod-card-row">{_cards_html}</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 三指标概览
# ============================================================
st.markdown("""
<div class="stat-row reveal">
    <div class="stat-card">
        <div class="label">品牌规范</div>
        <div class="value">5</div>
        <div class="sub">产品线严格把控</div>
    </div>
    <div class="stat-card">
        <div class="label">爆款范例</div>
        <div class="value">20</div>
        <div class="sub">篇言仓味标准笔记</div>
    </div>
    <div class="stat-card">
        <div class="label">AI 模型</div>
        <div class="value">V4</div>
        <div class="sub">DeepSeek 深度理解</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 主内容区：两 Tab
# ============================================================

tab1, tab2 = st.tabs([
    "内容品控",
    "爆文拆解",
])

# ============================================================
# TAB 1 — 内容品控
# ============================================================
with tab1:
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown('<p class="card-title">达人脚本审核</p>', unsafe_allow_html=True)
        st.markdown('<p class="card-desc">AI 对照言仓爆款范例和品牌规范，逐项审核脚本调性</p>', unsafe_allow_html=True)

        script_input = st.text_area(
            "粘贴小红书脚本",
            height=200,
            placeholder="例如：啊啊啊姐妹们这个线条小狗日历也太可爱了吧！必入！闭眼入！每一个都好好看...",
            key="qc_script",
            label_visibility="collapsed",
        )

        qc_btn = st.button("开始审核", type="primary", key="qc_btn",
                          disabled=not script_input.strip(), use_container_width=True)

    with c2:
        if qc_btn and script_input.strip():
            load_placeholder = st.empty()
            load_placeholder.markdown("""
            <div class="loading-container">
                <div class="loading-ring"></div>
                <div class="loading-text">AI 审核中，对照爆款范例…</div>
            </div>
            """, unsafe_allow_html=True)
            result = tone_check(script_input.strip())
            load_placeholder.empty()

            score = result.get("score", 0)
            if score >= 75:
                badge, verdict = "score-high", "通过 · 可直接发布"
            elif score >= 50:
                badge, verdict = "score-mid", "待调整 · 微调后发布"
            elif score >= 30:
                badge, verdict = "score-low", "不通过 · 需大幅改写"
            else:
                badge, verdict = "score-low", "内容不相关 · 无法审核"

            # 分数 + 结论
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.2rem;">
                <div class="score-pill {badge}">{score}</div>
                <div>
                    <span style="font-size:1.05rem;font-weight:600;color:#3d3226;">/100</span>
                    <span style="display:block;font-size:0.82rem;color:#8b7e6a;margin-top:0.15rem;">{verdict}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 问题点
            problems = [p for p in result.get("problems", []) if p.strip()]
            if problems:
                st.markdown('<p style="font-size:0.82rem;font-weight:600;color:#3d3226;margin-bottom:0.5rem;">问题点</p>', unsafe_allow_html=True)
                for p in problems:
                    st.markdown(f'<div class="problem-item"><span class="dot"></span><span>{p}</span></div>', unsafe_allow_html=True)

            # 润色版（低分不相关的内容不展示润色）
            if score >= 30:
                revised = result.get("revised_script", "")
                if revised and "失败" not in revised:
                    st.markdown('<p style="font-size:0.82rem;font-weight:600;color:#3d3226;margin:1rem 0 0.5rem;">润色后版本</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="script-card">{revised}</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align:center;padding:1.5rem;color:#b8a894;">
                    <p style="font-size:0.88rem;margin:0;">⚠️ 内容与言仓产品无关，无法生成润色版本</p>
                    <p style="font-size:0.78rem;margin:0.3rem 0 0 0;">请粘贴正经的小红书种草脚本</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-guide">
                <div class="icon">📝</div>
                <div class="title">如何使用</div>
                <p>1. 在左侧粘贴 KOL 脚本<br>2. 点击「开始审核」<br>3. AI 输出调性分 · 3 个问题点 · 完整润色版</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# TAB 2 — 爆文拆解
# ============================================================
with tab2:
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown('<p class="card-title">爆文拆解 & 套用</p>', unsafe_allow_html=True)
        st.markdown('<p class="card-desc">拆解小红书爆文结构，套用任意产品一键生成新脚本</p>', unsafe_allow_html=True)

        viral_note = st.text_area(
            "粘贴一篇小红书爆文",
            height=160,
            placeholder="例如：谁懂啊！！这个杯子真的长在我心巴上了...",
            key="viral_note",
            label_visibility="collapsed",
        )
        product_choice = st.text_input(
            "输入目标产品（任意品类均可）",
            placeholder="例如：线条小狗日历、香薰蜡烛、手冲咖啡壶...",
            key="product",
        )

        break_btn = st.button("拆解并生成新脚本", type="primary", key="break_btn",
                             disabled=not (viral_note.strip() and product_choice.strip()), use_container_width=True)

    with c2:
        if break_btn and viral_note.strip():
            load_placeholder = st.empty()
            load_placeholder.markdown("""
            <div class="loading-container">
                <div class="loading-ring"></div>
                <div class="loading-text">AI 正在拆解结构 + 生成 3 篇新脚本…</div>
            </div>
            """, unsafe_allow_html=True)
            result = hot_note_break(viral_note.strip(), product_choice)
            load_placeholder.empty()

            # 公式 + 钩子类型标签
            formula = result.get("formula", "")
            hook_type = result.get("hook_type", "")
            if formula or hook_type:
                st.markdown(
                    f'<div style="display:flex;gap:0.6rem;margin-bottom:0.8rem;">'
                    + (f'<span style="background:#f0ebe3;padding:0.25rem 0.7rem;border-radius:8px;font-size:0.78rem;color:#6b5e4a;">公式：{formula}</span>' if formula else "")
                    + (f'<span style="background:#f0ebe3;padding:0.25rem 0.7rem;border-radius:8px;font-size:0.78rem;color:#6b5e4a;">钩子：{hook_type}</span>' if hook_type else "")
                    + '</div>',
                    unsafe_allow_html=True,
                )

            structure = result.get("structure", {})
            segments = structure.get("segments", [])
            # Fallback: old format compatibility (hook/body1/body2/body3/ending)
            if not segments and structure.get("hook"):
                segments = [
                    {"label": "钩子", "quote": "", "analysis": structure.get("hook", "")},
                    {"label": "正文 1", "quote": "", "analysis": structure.get("body1", "")},
                    {"label": "正文 2", "quote": "", "analysis": structure.get("body2", "")},
                    {"label": "正文 3", "quote": "", "analysis": structure.get("body3", "")},
                    {"label": "结尾", "quote": "", "analysis": structure.get("ending", "")},
                ]
            if segments:
                st.markdown('<p style="font-size:0.82rem;font-weight:600;color:#3d3226;margin-bottom:0.5rem;">结构拆解</p>', unsafe_allow_html=True)
                segments_html = ""
                for seg in segments:
                    if not isinstance(seg, dict):
                        continue
                    label = seg.get("label", "")
                    quote = seg.get("quote", "")
                    analysis = seg.get("analysis", "")
                    quote_html = f'<br><span style="color:#b8a894;font-size:0.8rem;">原文：「{quote}」</span>' if quote else ""
                    segments_html += f'<p style="margin:0.3rem 0;"><b>{label}</b>：{analysis}{quote_html}</p>'
                st.markdown(f'<div class="script-card">{segments_html}</div>', unsafe_allow_html=True)

            scripts = result.get("scripts", [])
            if scripts:
                st.markdown(f'<p style="font-size:0.82rem;font-weight:600;color:#3d3226;margin:1rem 0 0.5rem;">{len(scripts)} 篇新脚本</p>', unsafe_allow_html=True)
                for i, s in enumerate(scripts, 1):
                    if s.strip():
                        with st.expander(f"脚本 {i}", expanded=(i == 1)):
                            st.markdown(f'<div class="script-card">{s}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-guide">
                <div class="icon">🔥</div>
                <div class="title">如何使用</div>
                <p>1. 在左侧粘贴任意小红书爆文<br>2. 选择言仓产品<br>3. AI 输出结构拆解 · 3 篇完整新脚本</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# 日历专区 — 底部网格展示言仓日历产品
# ============================================================
_cal_cards = ""
for _i, _img in enumerate(CAL_IMGS):
    _cal_cards += f'<div class="cal-card reveal" style="background: url(\'{_img}\') center/cover no-repeat;"></div>'
st.markdown(f"""
<div class="calendar-section">
    <p class="section-title">📅 言仓日历家族</p>
    <p class="section-sub">线条小狗 · 小刘鸭 · CHIIKAWA 联名周历 — 每一天都有小惊喜</p>
    <div class="cal-grid">{_cal_cards}</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# Footer
# ============================================================
st.markdown("""
<div class="app-footer">
    言仓文创 KOL 专属内容品控 & 复盘工作台 &nbsp;|&nbsp; Powered by DeepSeek V4
</div>
""", unsafe_allow_html=True)
