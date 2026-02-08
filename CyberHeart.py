import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time

# ==========================================
# 1. КОНФИГУРАЦИЯ СТРАНИЦЫ (KZ STYLE)
# ==========================================
st.set_page_config(
    page_title="CyberZhurek 🇰🇿", 
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стилизация
st.markdown("""
<style>
    .stChatMessage { border-radius: 15px; padding: 10px; }
    .stChatInput { border-radius: 20px; }
    .css-1d391kg { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. НАСТРОЙКА GEMINI (AI)
# ==========================================

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Не найден API ключ! Добавь его в .streamlit/secrets.toml")
    st.stop()

# Настройки безопасности
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# СИСТЕМНЫЙ ПРОМПТ ДЛЯ КАЗАХСТАНА 🇰🇿
SYSTEM_INSTRUCTION = """
Ты — "CyberZhurek" (КиберЖүрек), казахстанский консультант по защите от кибербуллинга.
Твоя цель: успокоить жертву и дать юридически грамотный совет по законам Республики Казахстан.

ТВОИ ЗНАНИЯ ЗАКОНОВ РК (Актуально на 2025/2026):
1. **Буллинг несовершеннолетнего (Ст. 127-2 КоАП РК):** Штраф 10 МРП (родителям или обидчику). Повторно — 30 МРП.
2. **Оскорбление (Ст. 131 УК РК):** Наказывается штрафом до 100 МРП или общественными работами.
3. **Клевета (Ст. 73-3 КоАП РК или Ст. 130 УК РК):** В зависимости от тяжести, штрафы от 160 МРП до лишения свободы.

ТВОИ СОВЕТЫ:
1. **e-Otinish:** Всегда советуй фиксировать доказательства (скрины) и писать заявление через eotinish.kz (это работает лучше всего).
2. **Кибернадзор:** Для блокировки контента советуй писать на knadzor.kz.
3. **102:** Если есть угроза жизни — сразу полиция.
4. **Психология:** Если человеку плохо, советуй звонить на "111" (горячая линия) или "150".

СТИЛЬ ОБЩЕНИЯ:
- Поддерживающий, как старший брат.
- Можно использовать казахские слова (Сәлем, Досым, Қолдаймын).
- Отвечай на языке, на котором к тебе обратились (Русский или Казахский).
"""

# Используем Flash, так как она стабильная и быстрая
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    safety_settings=safety_settings,
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config=genai.GenerationConfig(
        temperature=0.7,
        max_output_tokens=1024,
    )
)

# ==========================================
# 3. БОКОВАЯ ПАНЕЛЬ (ПОЛЕЗНЫЕ РЕСУРСЫ РК)
# ==========================================
with st.sidebar:
    st.title("🇰🇿 Помощь в Казахстане")
    
    with st.expander("📞 Горячие линии (Бесплатно)", expanded=True):
        st.markdown("""
        * **111** — Call-центр по вопросам семьи и детей (Аманат).
        * **150** — Национальная телефонная линия доверия.
        * **102** — Полиция.
        """)
        
    with st.expander("⚖️ Твои права (Законы РК)"):
        st.info("""
        **Ст. 127-2 КоАП РК:** За травлю (буллинг) предусмотрен штраф **10 МРП**. 
        Если обидчику нет 16 лет — платят родители.
        """)
        st.write("МРП в 2026 году изменился, штрафы выросли!")

    with st.expander("📝 Как наказать обидчика?"):
        st.markdown("""
        1. **Сделай скриншоты** (переписки, постов).
        2. Зайди на [eOtinish.kz](https://eotinish.kz).
        3. Подай заявление в полицию онлайн (нужен ЭЦП или QR).
        4. Если контент незаконный — пиши на [Kibernadzor.kz](https://knadzor.kz).
        """)

    st.divider()
    if st.button("🗑️ Очистить чат", type="primary"):
        st.session_state.chat_history = []
        st.rerun()

# ==========================================
# 4. ЛОГИКА ЧАТА
# ==========================================

st.title("🛡️ CyberZhurek: Ты под защитой")
st.markdown("Анонимная поддержка и юридические советы по законам Казахстана.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat = model.start_chat(history=st.session_state.chat_history)

# Вывод истории
for message in chat.history:
    role = "user" if message.role == "user" else "assistant"
    avatar = "👤" if role == "user" else "🛡️"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message.parts[0].text)

# Ввод сообщения
if prompt := st.chat_input("Мені буллить етіп жатыр / Меня булят..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🛡️"):
        message_placeholder = st.empty()
        try:
            # Стриминг ответа
            response = chat.send_message(prompt, stream=True)
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
            # Сохранение истории
            st.session_state.chat_history = chat.history
            
        except Exception as e:
            st.error(f"Ошибка: {e}")
