import os
import json
import certifi
import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

# ==========================================
# ENV
# ==========================================
os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")

# لو موديل خلصت حصته اليومية، يجرّب اللي بعده
MODELS = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"]


# ==========================================
# LLM
# ==========================================
@st.cache_resource
def get_models():
    return [
        ChatGoogleGenerativeAI(
            model=name,
            temperature=0,
            google_api_key=GOOGLE_API_KEY,
        )
        for name in MODELS
    ]


def to_text(content):
    if isinstance(content, list):
        return "".join(
            p.get("text", "") if isinstance(p, dict) else str(p) for p in content
        )
    return content


# ==========================================
# FUNCTIONS
# ==========================================
def get_capital(country: str) -> dict:
    prompt = (
        f"The country name may be in Arabic or English: '{country}'. "
        "Reply ONLY with a JSON object, no extra text, with keys: "
        '"country" (Arabic name), "capital" (English), "capital_ar" (Arabic).'
    )

    last_error = None
    for model in get_models():
        try:
            text = to_text(model.invoke(prompt).content)
            start, end = text.find("{"), text.rfind("}")
            return json.loads(text[start : end + 1])
        except Exception as e:
            last_error = e  # جرّب الموديل اللي بعده

    raise last_error


def get_weather(city: str) -> dict:
    r = requests.get(
        "https://api.weatherstack.com/current",
        params={"access_key": WEATHERSTACK_API_KEY, "query": city},
        timeout=15,
    ).json()

    if "current" not in r:
        raise ValueError("Could not fetch weather data")

    cur = r["current"]
    return {
        "temperature": f"{cur['temperature']}°C",
        "weather": cur["weather_descriptions"][0],
        "humidity": f"{cur['humidity']}%",
    }


@st.cache_data(ttl=600, show_spinner=False)
def lookup(country: str) -> dict:
    info = get_capital(country)
    info.update(get_weather(info["capital"]))
    return info


def safe_lookup(country: str):
    try:
        return lookup(country), None
    except Exception as e:
        return None, str(e)


# ==========================================
# UI
# ==========================================
st.set_page_config(page_title="Capital & Weather", page_icon="🌍", layout="wide")

st.title("🌍 Capital & Weather")
st.caption("اكتب دولة أو أكتر (عربي أو English) وافصل بينهم بفاصلة")

countries_input = st.text_input("الدول", placeholder="مصر, India, France")

if st.button("🔍 ابحث", type="primary"):
    countries = [
        c.strip()
        for c in countries_input.replace("،", ",").split(",")
        if c.strip()
    ]

    if not countries:
        st.warning("اكتب اسم دولة واحدة على الأقل.")
        st.stop()

    get_models()  # تجهيز الموديلات قبل ما الـ threads تبدأ

    with st.spinner("جاري البحث..."):
        with ThreadPoolExecutor(max_workers=len(countries)) as pool:
            results = list(pool.map(safe_lookup, countries))

    cols = st.columns(min(len(countries), 3))

    for i, (country, (info, err)) in enumerate(zip(countries, results)):
        with cols[i % len(cols)]:
            if err:
                st.error(f"{country}: حصل خطأ ({err})")
                continue

            with st.container(border=True):
                st.subheader(info["country"])
                st.markdown(f"🏛️ **العاصمة:** {info['capital_ar']} ({info['capital']})")
                c1, c2 = st.columns(2)
                c1.metric("🌡️ الحرارة", info["temperature"])
                c2.metric("💧 الرطوبة", info["humidity"])
                st.info(f"☁️ الجو: {info['weather']}")