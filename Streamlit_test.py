import streamlit as st
import pandas as pd
import plotly.express as px

def mySql():
    conn = st.connection('mysql', type='sql')
    df = conn.query('SELECT Alue, `2015`,`2016`,`2017`,`2018`,`2019`,`2020`,`2021`,`2022`,`2023`,`2024` FROM vakiluku;', ttl=600)
    return df

def main():
    st.title("Kuntien väkiluvut 2015-2024")
    df = mySql()
    df = df[df["Alue"] != "Alue"]
    df = pd.concat([df[df["Alue"]=="KOKO MAA"], df[df["Alue"]!="KOKO MAA"]])
    default_kunta = "KOKO MAA"
    alueet = df["Alue"].unique()
    if default_kunta in alueet:
        default_index = list(alueet).index(default_kunta)
    else:
        default_index = 0
    kunta = st.selectbox("Valitse kunta", alueet, index=default_index)
    df_kunta = df[df["Alue"] == kunta].iloc[0]
    df_plot = pd.DataFrame({
        "Vuosi": [str(year) for year in range(2015, 2025)],
        "Väkiluku": df_kunta[1:].values
    })
    fig = px.line(df_plot, x="Vuosi", y="Väkiluku", title=f"Väkiluku: {kunta}")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
