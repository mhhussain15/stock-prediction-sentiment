import streamlit as st
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go

# 🔑 PUT YOUR NEWSAPI KEY HERE
NEWS_API_KEY = "65a05064da4942a2bf93a2a492e19e11"

def run():

    st.header("📰 Real-Time Market Sentiment Analysis")

    stock_options = {
        "Reliance": ["Reliance", "Reliance Industries", "RIL"],
        "TCS": ["TCS", "Tata Consultancy Services"],
        "Infosys": ["Infosys"],
        "HDFC Bank": ["HDFC Bank"],
        "ICICI Bank": ["ICICI Bank"],
        "SBI": ["State Bank of India", "SBI"],
        "ONGC": ["ONGC"],
        "Tata Motors": ["Tata Motors"]
    }

    selected_stock = st.selectbox("Select Stock", list(stock_options.keys()))
    query = stock_options[selected_stock][0]

    if st.button("Fetch & Analyze News"):

        url = (
            f"https://newsapi.org/v2/everything?"
            f'q="{query}" AND (stock OR shares OR earnings OR results OR profit OR revenue OR market)&'
            f"language=en&"
            f"sortBy=publishedAt&"
            f"pageSize=20&"
            f"apiKey={NEWS_API_KEY}"
        )   

        response = requests.get(url)
        data = response.json()

        articles = data.get("articles", [])

        if not articles:
            st.warning("No news articles found.")
            return
        
        filtered_articles = []

        keywords = stock_options[selected_stock]  # list of company keywords

        for article in articles:
            title = article["title"].lower()

            if any(k.lower() in title for k in keywords):
                filtered_articles.append(article)

        articles = filtered_articles

        if not articles:
            st.warning("No relevant company-specific news found.")
            return

        analyzer = SentimentIntensityAnalyzer()
        sentiment_results = []

        for article in articles:
            title = article["title"]
            source = article["source"]["name"]

            score = analyzer.polarity_scores(title)["compound"]

            if score >= 0.05:
                label = "Positive"
            elif score <= -0.05:
                label = "Negative"
            else:
                label = "Neutral"

            sentiment_results.append({
                "Source": source,
                "Headline": title,
                "Sentiment Score": score,
                "Sentiment": label
            })

        df = pd.DataFrame(sentiment_results)

        st.subheader("📊 News Sentiment Table")
        st.dataframe(df)

        avg_score = df["Sentiment Score"].mean()

        pos = (df["Sentiment"] == "Positive").sum()
        neg = (df["Sentiment"] == "Negative").sum()
        neu = (df["Sentiment"] == "Neutral").sum()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average Sentiment", f"{avg_score:.3f}")
        col2.metric("Positive", pos)
        col3.metric("Negative", neg)
        col4.metric("Neutral", neu)

        # 📊 Gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_score,
            title={'text': "Overall Market Mood"},
            gauge={'axis': {'range': [-1, 1]}}
        ))
        st.plotly_chart(fig)

        # 📊 Pie Chart
        fig2 = px.pie(df, names="Sentiment", title="Sentiment Distribution")
        st.plotly_chart(fig2)

        # 📈 Investor Insight
        st.subheader("📈 Investor Insight")

        if avg_score > 0.2:
            st.success("Strong Bullish News Sentiment 📈")
        elif avg_score > 0:
            st.info("Mild Positive Sentiment")
        elif avg_score < -0.2:
            st.error("Strong Bearish Sentiment 📉")
        else:
            st.warning("Mixed / Neutral Sentiment")
            
if __name__ == "__main__":
    run()
