import streamlit as st
from google import genai

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IRCTC Rail Assistant",
    page_icon="🚄",
    layout="centered",
)

# ══════════════════════════════════════════════════════════════════════════════
#  ▼▼▼  EDIT ONLY THESE TWO LINES  ▼▼▼
API_KEY = "AIzaSyCGmQjLwv-_77eqr7lZuRnjHCEM5Mnc66U"    # ← paste your Gemini API key here
KB_FILE = "train_dataset.txt"     # ← path to your knowledge-base file
# ══════════════════════════════════════════════════════════════════════════════

# ── Load knowledge base ────────────────────────────────────────────────────────
@st.cache_data
def load_kb(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.warning(f"⚠️  Knowledge base file '{path}' not found. Running without KB.")
        return ""

kb = load_kb(KB_FILE)

SYSTEM_PROMPT = f"""
You are an IRCTC Customer Care executive. Your job is to answer customer questions politely.
If a question is outside your knowledge base, say you don't have that information.
Only use the knowledge base below to answer questions.

KNOWLEDGE BASE:
{kb}
"""

# ── Gemini call ────────────────────────────────────────────────────────────────
def ask_gemini(prior_messages: list, user_text: str) -> str:
    sdk_history = [
        {"role": "user" if m["role"] == "user" else "model",
         "parts": [{"text": m["content"]}]}
        for m in prior_messages
    ]
    client  = genai.Client(api_key=API_KEY)
    session = client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": SYSTEM_PROMPT},
        history=sdk_history,
    )
    return session.send_message(user_text).text

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages: list = []

# ── Full CSS + HTML UI injected via st.markdown ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:       #0a0f1e;
  --card:     #12203a;
  --border:   #1e3358;
  --accent:   #ff6b35;
  --accent2:  #00d4ff;
  --accent3:  #7c3aed;
  --text:     #e8f0fe;
  --muted:    #6b89b8;
  --bot-bub:  #132040;
  --rail:     #1a4a8a;
}

/* ── Reset Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: var(--bg) !important; }
.stChatMessage { background: transparent !important; border: none !important; }

/* ── Animated background ── */
.stApp::before {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 80% 60% at 20% 10%, rgba(26,74,138,0.25) 0%, transparent 60%),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(255,107,53,0.12) 0%, transparent 55%),
    repeating-linear-gradient(90deg, transparent, transparent 119px, rgba(30,51,88,0.3) 120px);
}

/* ── Moving track line at bottom ── */
.track-anim {
  position: fixed; bottom: 60px; left: 0; right: 0; height: 2px;
  background: repeating-linear-gradient(90deg,
    var(--accent) 0, var(--accent) 30px,
    transparent 30px, transparent 60px);
  animation: trackScroll 2.5s linear infinite;
  opacity: 0.3; z-index: 0; pointer-events: none;
}
@keyframes trackScroll { from { background-position: 0; } to { background-position: 60px; } }

/* ── Header ── */
.rail-header {
  position: relative; z-index: 10;
  display: flex; align-items: center; gap: 16px;
  padding: 16px 28px;
  background: rgba(14,22,40,0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 4px 40px rgba(0,0,0,0.5);
  font-family: 'DM Sans', sans-serif;
}
.logo-wrap { position: relative; width: 50px; height: 50px; flex-shrink: 0; }
.logo-ring {
  position: absolute; inset: 0; border-radius: 50%;
  border: 2px solid transparent;
  background: conic-gradient(var(--accent), var(--accent2), var(--accent3), var(--accent)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out; mask-composite: exclude;
  animation: spinRing 4s linear infinite;
}
@keyframes spinRing { to { transform: rotate(360deg); } }
.logo-icon {
  position: absolute; inset: 6px;
  background: linear-gradient(135deg, var(--rail), #0a1830);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
}
.hdr-title {
  font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.2rem;
  background: linear-gradient(135deg, #fff 30%, var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hdr-sub { font-size: 0.72rem; color: var(--muted); letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px; }
.hdr-right { margin-left: auto; }
.status-badge {
  display: flex; align-items: center; gap: 8px;
  background: rgba(0,212,255,0.08); border: 1px solid rgba(0,212,255,0.2);
  border-radius: 999px; padding: 5px 14px;
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #22c55e; box-shadow: 0 0 8px #22c55e;
  animation: pulseGlow 2s ease-in-out infinite;
}
@keyframes pulseGlow {
  0%,100% { box-shadow: 0 0 8px #22c55e; }
  50%      { box-shadow: 0 0 18px #22c55e, 0 0 30px rgba(34,197,94,0.4); }
}
.status-lbl { font-size: 0.7rem; color: var(--accent2); font-weight: 500; }

/* ── Welcome card ── */
.welcome-card {
  background: linear-gradient(135deg, rgba(26,74,138,0.3), rgba(255,107,53,0.1));
  border: 1px solid rgba(0,212,255,0.15); border-radius: 20px;
  padding: 26px; text-align: center; margin: 20px auto; max-width: 680px;
  animation: slideDown 0.7s cubic-bezier(.16,1,.3,1) both;
  font-family: 'DM Sans', sans-serif;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: none; } }
.wc-emoji { font-size: 2.2rem; margin-bottom: 8px; }
.wc-title {
  font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 700;
  background: linear-gradient(135deg, #fff, var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}
.wc-sub { font-size: 0.85rem; color: var(--muted); line-height: 1.6; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-top: 14px; }
.chip {
  background: rgba(255,107,53,0.1); border: 1px solid rgba(255,107,53,0.3);
  color: var(--accent); border-radius: 999px; padding: 5px 14px;
  font-size: 0.76rem; cursor: pointer; transition: all 0.25s;
  font-family: 'DM Sans', sans-serif;
}
.chip:hover { background: rgba(255,107,53,0.25); transform: translateY(-2px); }

/* ── Message bubbles ── */
.msg-row {
  display: flex; align-items: flex-end; gap: 10px;
  margin: 10px auto; max-width: 720px; padding: 0 16px;
  animation: msgIn 0.4s cubic-bezier(.16,1,.3,1) both;
  font-family: 'DM Sans', sans-serif;
}
@keyframes msgIn { from { opacity: 0; transform: translateY(16px) scale(0.97); } to { opacity: 1; transform: none; } }
.msg-row.user { flex-direction: row-reverse; }

.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; flex-shrink: 0;
}
.av-bot {
  background: linear-gradient(135deg, var(--rail), #0a1830);
  border: 1px solid rgba(0,212,255,0.3);
  box-shadow: 0 0 12px rgba(0,212,255,0.15);
}
.av-user {
  background: linear-gradient(135deg, var(--accent), #e85d25);
  box-shadow: 0 0 12px rgba(255,107,53,0.3);
}
.bubble { max-width: 74%; padding: 12px 16px; border-radius: 16px; font-size: 0.88rem; line-height: 1.65; }
.b-bot  { background: var(--bot-bub); border: 1px solid var(--border); border-bottom-left-radius: 4px; color: var(--text); }
.b-user { background: linear-gradient(135deg, var(--accent), #e55a20); border-bottom-right-radius: 4px; color: #fff; box-shadow: 0 4px 18px rgba(255,107,53,0.25); }
.msg-time { font-size: 0.65rem; color: var(--muted); margin-top: 4px; padding: 0 4px; }
.msg-row.user .msg-time { text-align: right; }

/* ── Typing indicator ── */
.typing-dots { display: flex; align-items: center; gap: 5px; padding: 12px 16px; background: var(--bot-bub); border: 1px solid var(--border); border-radius: 16px; border-bottom-left-radius: 4px; }
.typing-dots span { width: 7px; height: 7px; border-radius: 50%; background: var(--muted); animation: typeBounce 1.2s ease-in-out infinite; }
.typing-dots span:nth-child(2) { animation-delay: .2s; }
.typing-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes typeBounce { 0%,60%,100% { transform: translateY(0); opacity:.4; } 30% { transform: translateY(-7px); opacity:1; } }

/* ── Streamlit chat input override ── */
section[data-testid="stChatInput"],
.stChatInputContainer {
  background: rgba(10,15,30,0.95) !important;
  border-top: 1px solid var(--border) !important;
  backdrop-filter: blur(20px) !important;
  padding: 14px 20px !important;
}
section[data-testid="stChatInput"] textarea {
  background: rgba(18,32,58,0.9) !important;
  border: 1px solid rgba(255,107,53,0.35) !important;
  border-radius: 14px !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.9rem !important;
  caret-color: var(--accent) !important;
}
section[data-testid="stChatInput"] textarea:focus {
  border-color: var(--accent2) !important;
  box-shadow: 0 0 0 3px rgba(0,212,255,0.1) !important;
}
section[data-testid="stChatInput"] textarea::placeholder { color: var(--muted) !important; }
section[data-testid="stChatInput"] button {
  background: linear-gradient(135deg, var(--accent), #e55a20) !important;
  border-radius: 10px !important;
  border: none !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
</style>

<!-- Moving track line -->
<div class="track-anim"></div>

<!-- Header -->
<div class="rail-header">
  <div class="logo-wrap">
    <div class="logo-ring"></div>
    <div class="logo-icon">🚄</div>
  </div>
  <div>
    <div class="hdr-title">IRCTC Rail Assistant</div>
    <div class="hdr-sub">Powered by Gemini · Customer Care</div>
  </div>
  <div class="hdr-right">
    <div class="status-badge">
      <div class="status-dot"></div>
      <span class="status-lbl">Live</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Welcome card (only on fresh load) ─────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
      <div class="wc-emoji">👋</div>
      <div class="wc-title">Namaste! How can I help you?</div>
      <div class="wc-sub">I'm your AI-powered IRCTC customer care assistant.<br>
        Ask me anything about trains, bookings, PNR status, or schedules.</div>
      <div class="chips">
        <span class="chip">🕐 Train timings</span>
        <span class="chip">🎟 Book a ticket</span>
        <span class="chip">📋 PNR status</span>
        <span class="chip">❌ Cancel ticket</span>
        <span class="chip">🛏 Berth types</span>
        <span class="chip">💰 Refund policy</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Render previous messages ───────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-row user">
          <div>
            <div class="bubble b-user">{msg["content"]}</div>
            <div class="msg-time">{msg.get("time","")}</div>
          </div>
          <div class="avatar av-user">👤</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row">
          <div class="avatar av-bot">🚄</div>
          <div>
            <div class="bubble b-bot">{msg["content"]}</div>
            <div class="msg-time">IRCTC AI · {msg.get("time","")}</div>
          </div>
        </div>""", unsafe_allow_html=True)

# ── Chat input ─────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask about trains, schedules, booking…"):

    import datetime
    now = datetime.datetime.now().strftime("%I:%M %p")

    # Save & show user message
    st.session_state.messages.append({"role": "user", "content": user_input, "time": now})
    st.markdown(f"""
    <div class="msg-row user">
      <div>
        <div class="bubble b-user">{user_input}</div>
        <div class="msg-time">{now}</div>
      </div>
      <div class="avatar av-user">👤</div>
    </div>""", unsafe_allow_html=True)

    # Typing indicator
    typing_ph = st.empty()
    typing_ph.markdown("""
    <div class="msg-row">
      <div class="avatar av-bot">🚄</div>
      <div class="typing-dots"><span></span><span></span><span></span></div>
    </div>""", unsafe_allow_html=True)

    # Get reply
    reply = ask_gemini(st.session_state.messages[:-1], user_input)

    # Show reply
    typing_ph.empty()
    st.session_state.messages.append({"role": "assistant", "content": reply, "time": now})
    st.markdown(f"""
    <div class="msg-row">
      <div class="avatar av-bot">🚄</div>
      <div>
        <div class="bubble b-bot">{reply}</div>
        <div class="msg-time">IRCTC AI · {now}</div>
      </div>
    </div>""", unsafe_allow_html=True)