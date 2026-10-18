# 🌍 Capital & Weather

A Streamlit app that takes one or more countries (Arabic or English) and returns each country's capital with its current weather.

## ✨ Features

- 🌐 Arabic & English country names (e.g. `مصر`, `India`)
- 🔢 Multiple countries at once, separated by a comma
- ⚡ Parallel lookups with `ThreadPoolExecutor`
- 💾 10-minute result caching
- 🔁 Automatic fallback between Gemini models when a quota is exhausted

## 🛠️ Tech Stack

- Python
- Streamlit
- LangChain + Google Gemini
- Weatherstack API

## 🚀 Getting Started

**1. Clone the repo**
```bash
git clone https://github.com/brahemnabil59-tech/capital-weather-app.git
cd capital-weather-app
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API keys**

Create a `.env` file (see `.env.example`):
```env
GOOGLE_API_KEY=your_gemini_key
WEATHERSTACK_API_KEY=your_weatherstack_key
```

- Gemini key: [Google AI Studio](https://aistudio.google.com/)
- Weatherstack key: [weatherstack.com](https://weatherstack.com/)

**4. Run**
```bash
streamlit run main.py
```

Then open http://localhost:8501

## 💡 Example

Input:
```
مصر, India, France
```

Output: a card per country showing the capital, temperature, humidity, and weather.

## 🔄 How It Works

1. Gemini returns the capital of the country as JSON.
2. The capital is sent to the Weatherstack API for current weather.
3. Results are displayed as cards.

## 👤 Author

**Ebrahem Nabil** — AI Engineer
[GitHub](https://github.com/brahemnabil59-tech)
