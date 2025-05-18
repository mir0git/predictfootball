import pandas as pd
import streamlit as st

st.set_page_config(page_title="🔮 Prédicteur basé sur les cotes 1X2", layout="wide")
st.title("🔮 Prédicteur basé sur les cotes 1X2")

uploaded_file = st.file_uploader("📂 Cliquez ici pour importer votre fichier Excel (football.xlsx)", type=["xlsx"])

cote1, coteX, cote2 = 0.0, 0.0, 0.0
cote1 = st.sidebar.number_input("Cote 1 (domicile)", value=cote1, min_value=0.0, step=0.01, format="%.2f")
coteX = st.sidebar.number_input("Cote X (nul)", value=coteX, min_value=0.0, step=0.01, format="%.2f")
cote2 = st.sidebar.number_input("Cote 2 (extérieur)", value=cote2, min_value=0.0, step=0.01, format="%.2f")

if uploaded_file:
    @st.cache_data
    def load_data(file):
        df = pd.read_excel(file)

        def extract_info(score):
            try:
                home, away = map(int, str(score).split("-"))
                if home > away:
                    result = "1"
                elif home < away:
                    result = "2"
                else:
                    result = "N"
                return pd.Series([result, home + away])
            except:
                return pd.Series([None, None])

        df[["Vainqueur", "Total_Buts"]] = df["Score"].apply(extract_info)
        return df

    df = load_data(uploaded_file)

    if st.sidebar.button("Analyser"):
        conditions = pd.Series([True] * len(df))
        if cote1 != 0.0:
            conditions &= (df["Cote 1"] == cote1)
        if coteX != 0.0:
            conditions &= (df["Cote X"] == coteX)
        if cote2 != 0.0:
            conditions &= (df["Cote 2"] == cote2)

        data = df[conditions]
        total = len(data)

        if total == 0:
            st.warning("Aucun match trouvé pour cette combinaison de cotes.")
        else:
            pct = lambda cond: round(len(data[data["Vainqueur"] == cond]) / total * 100, 2)
            buts_moyens = round(data["Total_Buts"].mean(), 2)
            over_2_5 = round(len(data[data["Total_Buts"] > 2.5]) / total * 100, 2)
            over_1_5 = round(len(data[data["Total_Buts"] > 1.5]) / total * 100, 2)

            data[["Buts_Dom", "Buts_Ext"]] = data["Score"].str.split("-", expand=True).astype(float)
            moy_dom = round(data["Buts_Dom"].mean(), 2)
            med_dom = round(data["Buts_Dom"].median(), 2)
            moy_ext = round(data["Buts_Ext"].mean(), 2)
            med_ext = round(data["Buts_Ext"].median(), 2)

            st.subheader(f"📊 {total} matchs trouvés pour cette configuration")
            st.metric("Victoire domicile", f"{pct('1')}%")
            st.metric("Match nul", f"{pct('N')}%")
            st.metric("Victoire extérieur", f"{pct('2')}%")

            st.subheader("⚽ Analyse des buts")
            st.write(f"Moyenne de buts : **{buts_moyens}**")
            st.write(f"Over 2.5 buts : **{over_2_5}%**")
            st.write(f"Under 2.5 buts : **{round(100 - over_2_5, 2)}%**")
            st.write(f"Over 1.5 buts : **{over_1_5}%**")

            st.markdown("---")
            st.subheader("📌 Moyennes & Médianes par équipe")
            st.write(f"Buts équipe domicile - Moyenne : **{moy_dom}**, Médiane : **{med_dom}**")
            st.write(f"Buts équipe extérieur - Moyenne : **{moy_ext}**, Médiane : **{med_ext}**")

            st.markdown("---")
            st.subheader("📚 Analyse par compétition")
            top_competitions = data["Compétition"].value_counts().head(5)
            st.write("Top compétitions trouvées pour ces cotes :")
            st.dataframe(top_competitions)

            st.markdown("---")
            st.subheader("📈 Valeur réelle vs probabilité de la cote")

            def afficher_valeur(cote, real_pct, label):
                if cote > 0:
                    prob = round(100 / cote, 2)
                    delta = round(real_pct - prob, 2)
                    if delta > 5:
                        note = "🔥 VALUE détectée"
                        color = "green"
                    elif delta < -5:
                        note = "⚠️ Surcote, à éviter"
                        color = "red"
                    else:
                        note = "🟡 Équilibré"
                        color = "orange"

                    st.markdown(
                        f"<span style='font-weight:bold'>{label}</span> : probabilité implicite **{prob}%**, réalité observée **{real_pct}%**<br>"
                        f"<span style='color:{color}; font-weight:bold'>{note}</span>",
                        unsafe_allow_html=True
                    )

            afficher_valeur(cote1, pct("1"), "Cote 1")
            afficher_valeur(coteX, pct("N"), "Cote X")
            afficher_valeur(cote2, pct("2"), "Cote 2")

else:
    st.info("🟡 Importez un fichier Excel pour commencer l'analyse.")
