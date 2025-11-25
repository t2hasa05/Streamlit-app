import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector
from dotenv import load_dotenv
import os
import requests
from streamlit_autorefresh import st_autorefresh

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_HOST = os.getenv("MYSQL_HOST")

def hae_vakiluvut():
    conn = st.connection('mysql', type='sql')
    df = conn.query('SELECT Alue, `2015`,`2016`,`2017`,`2018`,`2019`,`2020`,`2021`,`2022`,`2023`,`2024` FROM vakiluku;', ttl=600)
    return df

def hae_saadata():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

    df = pd.read_sql('SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 50',conn)
    conn.close()
    return df

def main():
    st.title("Data analysis")

    tab1, tab2, tab3 = st.tabs(["📊 Väkiluvut", "🌤️ Säädata", "🐱 Random cat facts"])

    with tab1:
        st.header("Kuntien väkiluvut (2015-2024)")

        df = hae_vakiluvut()
        df = df[df["Alue"] != "Alue"]
        df = pd.concat([df[df["Alue"]=="KOKO MAA"], df[df["Alue"]!="KOKO MAA"]])

        default_kunta = "KOKO MAA"
        alueet = df["Alue"].unique()
        default_index = list(alueet).index(default_kunta) if default_kunta in alueet else 0

        kunta = st.selectbox("Valitse kunta", alueet, index=default_index)
        df_kunta = df[df["Alue"] == kunta].iloc[0]
        df_plot = pd.DataFrame({
            "Vuosi": [str(year) for year in range(2015, 2025)],
            "Väkiluku": df_kunta[1:].values
        })

        fig = px.line(df_plot, x="Vuosi", y="Väkiluku", title=f"Väkiluku: {kunta}")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Sää Oulussa")
        st_autorefresh(interval=60000, key="weather_refresh")
        df_weather = hae_saadata()
        st.dataframe(df_weather[["city", "temperature", "description", "timestamp"]])

    with tab3:
        st.header("Random cat fact")

        # Hae satunnainen fakta
        def get_cat_fact():
            response = requests.get("https://catfact.ninja/fact")
            if response.status_code == 200:
                return response.json()['fact']
            else:
                return "Faktan haku epäonnistui 😿"

        def update_fact():
            st.session_state.cat_fact = get_cat_fact()

        # Näytetään ensimmäinen fakta sivun latauksessa
        if 'cat_fact' not in st.session_state:
            st.session_state.cat_fact = get_cat_fact()

        st.write(st.session_state.cat_fact)

        # Nappi uuden faktan hakemiseen
        st.button("Get a new fact", on_click=update_fact)

if __name__ == "__main__":
    main()
