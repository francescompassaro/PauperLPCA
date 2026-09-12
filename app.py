import streamlit as st
import pandas as pd
import plotly.express as px

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Dashboard Torneo Magic",
    page_icon="🃏",
    layout="wide"
)

# URL CSV diretti dei fogli Google Sheets
url_dashboard_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQm6a3xy0G0f7M9BSK0zdlEqt_zkcegQXjmbS5CYiXDKQCBCm2voWanMfbA--5CrDtrESrOdE50fdex/pub?gid=820700615&single=true&output=csv"
url_matchup_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQm6a3xy0G0f7M9BSK0zdlEqt_zkcegQXjmbS5CYiXDKQCBCm2voWanMfbA--5CrDtrESrOdE50fdex/pub?gid=835196889&single=true&output=csv" # Sostituisci MATCHUP_GID_QUI con il GID del foglio matchup


# --- MENU LATERALE ---
st.sidebar.title("📌 Menu Navigazione")
pagina = st.sidebar.radio("Seleziona una sezione:", ["Dashboard Generale", "Dettaglio Tappe", "Analisi Matchup"])

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Aggiorna Dati"):
    st.rerun()

try:
    # Lettura dei dati del foglio Dashboard
    df = pd.read_csv(url_dashboard_csv)
    
    # Pulizia colonne
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Giocatore", "Nome Deck"])
    
    # Conversione numerica
    df["W"] = pd.to_numeric(df["W"], errors="coerce").fillna(0)
    df["L"] = pd.to_numeric(df["L"], errors="coerce").fillna(0)
    df["D"] = pd.to_numeric(df["D"], errors="coerce").fillna(0)
    df["punteggio"] = pd.to_numeric(df["punteggio"], errors="coerce").fillna(0)
    if "N. tappa" in df.columns:
        df["N. tappa"] = pd.to_numeric(df["N. tappa"], errors="coerce")

    # ==========================================
    # PAGINA 1: DASHBOARD GENERALE
    # ==========================================
    if pagina == "Dashboard Generale":
        st.title("🃏 Dashboard Torneo Magic - Statistiche & Grafici")

        st.header("🏆 Classifica Generale")
        
        classifica = df.groupby("Giocatore").agg(
            Punti_Totali=("punteggio", "sum"),
            Vittorie=("W", "sum"),
            Sconfitte=("L", "sum"),
            Pareggi=("D", "sum")
        ).reset_index()

        classifica = classifica.sort_values(by="Punti_Totali", ascending=False).reset_index(drop=True)
        classifica.insert(0, "Posizione_Num", range(1, len(classifica) + 1))
        classifica["Posizione"] = classifica["Posizione_Num"].apply(lambda x: f"{x}°")
        
        tabella = classifica[["Posizione", "Giocatore", "Punti_Totali", "Vittorie", "Sconfitte", "Pareggi"]].rename(
            columns={"Punti_Totali": "Punti Totali", "Vittorie": "W", "Sconfitte": "L", "Pareggi": "D"}
        )

        def stile_classifica(row):
            pos = row["Posizione"]
            if pos == "1°":
                return ['background-color: #D4AF37; color: #111111; font-weight: bold; border-bottom: 2px solid #997A15'] * len(row)
            elif pos in ["2°", "3°", "4°"]:
                return ['background-color: #E6E8FA; color: #1A202C; font-weight: bold; border-bottom: 1px solid #CBD5E0'] * len(row)
            else:
                return ['background-color: #F7FAFC; color: #2D3748'] * len(row)

        tabella_styled = tabella.style.apply(stile_classifica, axis=1)

        col1, col2 = st.columns([1.3, 1])
        with col1:
            st.dataframe(tabella_styled, use_container_width=True, hide_index=True)

        st.markdown("---")

        st.header("📊 Analisi Mazzi (Grafici a Torta)")

        presenze_deck = df["Nome Deck"].value_counts().reset_index()
        presenze_deck.columns = ["Nome Deck", "Presenze"]

        stats_deck = df.groupby("Nome Deck").agg(
            Vittorie=("W", "sum"),
            Sconfitte=("L", "sum")
        ).reset_index()
        
        stats_deck["Partite Totali"] = stats_deck["Vittorie"] + stats_deck["Sconfitte"]
        stats_deck = stats_deck[stats_deck["Partite Totali"] > 0]
        stats_deck["Win Rate (%)"] = (stats_deck["Vittorie"] / stats_deck["Partite Totali"] * 100).round(2)

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("🥧 Presenza Mazzi nel Meta (%)")
            fig_pie_meta = px.pie(
                presenze_deck,
                names="Nome Deck",
                values="Presenze",
                title="Quota di Presenza dei Mazzi nel Torneo",
                hole=0.35,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie_meta.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie_meta, use_container_width=True)

        with col4:
            st.subheader("🥧 Win Rate dei Mazzi (%)")
            fig_pie_winrate = px.pie(
                stats_deck,
                names="Nome Deck",
                values="Win Rate (%)",
                title="Distribuzione del Win Rate per Mazzo",
                hole=0.35,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie_winrate.update_traces(textinfo='value+label', texttemplate='%{label}: %{value:.1f}%')
            st.plotly_chart(fig_pie_winrate, use_container_width=True)

    # ==========================================
    # PAGINA 2: DETTAGLIO TAPPE
    # ==========================================
    elif pagina == "Dettaglio Tappe":
        st.title("📅 Dettaglio Giocatori per Season & Tappa")

        seasons_disponibili = ["Tutte"] + list(df["Nome Season"].dropna().unique()) if "Nome Season" in df.columns else ["Tutte"]
        season_selezionata = st.sidebar.selectbox("Seleziona Season:", seasons_disponibili)

        df_filtrato_season = df if season_selezionata == "Tutte" else df[df["Nome Season"] == season_selezionata]

        if "N. tappa" in df_filtrato_season.columns:
            tappe_disponibili = sorted(df_filtrato_season["N. tappa"].dropna().unique().astype(int))
            tappa_selezionata = st.sidebar.selectbox("Seleziona N. Tappa:", tappe_disponibili, index=len(tappe_disponibili)-1 if len(tappe_disponibili) > 0 else 0)
            
            df_tappa = df_filtrato_season[df_filtrato_season["N. tappa"] == tappa_selezionata].copy()
            
            if "posizione" in df_tappa.columns:
                df_tappa["posizione"] = pd.to_numeric(df_tappa["posizione"], errors="coerce")
                df_tappa = df_tappa.sort_values(by="posizione", ascending=True)
            else:
                df_tappa = df_tappa.sort_values(by="punteggio", ascending=False)
            
            colonne_mostra = ["posizione", "Giocatore", "Nome Deck", "W", "L", "D", "punteggio"]
            colonne_esistenti = [c for c in colonne_mostra if c in df_tappa.columns]
            
            df_vista_tappa = df_tappa[colonne_esistenti].rename(columns={
                "posizione": "Posizione",
                "Nome Deck": "Mazzo",
                "punteggio": "Punti"
            })
            
            st.subheader(f"Risultati Tappa {tappa_selezionata} - Season: {season_selezionata}")
            
            col_t1, col_t2 = st.columns([1.6, 1])
            with col_t1:
                st.dataframe(df_vista_tappa, use_container_width=True, hide_index=True)

    # ==========================================
    # PAGINA 3: ANALISI MATCHUP
    # ==========================================
    elif pagina == "Analisi Matchup":
        st.title("⚔️ Matrice dei Matchup (Win Rate tra Mazzi)")
        
        try:
            df_matchup = pd.read_csv(url_matchup_csv)
            df_matchup.columns = df_matchup.columns.str.strip()
            
            rename_dict = {}
            for col in df_matchup.columns:
                if col.lower() in ["season", "nome season", "nome_season"]:
                    rename_dict[col] = "season"
                elif col.lower() in ["tappa", "n. tappa", "n_tappa"]:
                    rename_dict[col] = "tappa"
            df_matchup.rename(columns=rename_dict, inplace=True)

            st.sidebar.subheader("🎯 Filtri Matchup")
            seasons_m = ["Tutte"] + list(df_matchup["season"].dropna().unique()) if "season" in df_matchup.columns else ["Tutte"]
            season_m_sel = st.sidebar.selectbox("Season (Matchup):", seasons_m)
            
            df_m_filtrato = df_matchup if season_m_sel == "Tutte" else df_matchup[df_matchup["season"] == season_m_sel]
            
            tappe_m = ["Tutte"] + list(df_m_filtrato["tappa"].dropna().unique()) if "tappa" in df_m_filtrato.columns else ["Tutte"]
            tappa_m_sel = st.sidebar.selectbox("Tappa (Matchup):", tappe_m)
            
            if tappa_m_sel != "Tutte":
                df_m_filtrato = df_m_filtrato[df_m_filtrato["tappa"] == tappa_m_sel]

            if {"Deck_A", "Deck_B", "W_A", "W_B"}.issubset(df_m_filtrato.columns):
                
                df_m_filtrato["W_A"] = pd.to_numeric(df_m_filtrato["W_A"], errors="coerce").fillna(0)
                df_m_filtrato["W_B"] = pd.to_numeric(df_m_filtrato["W_B"], errors="coerce").fillna(0)
                df_m_filtrato = df_m_filtrato.dropna(subset=["Deck_A", "Deck_B"])
                
                mazzi = sorted(list(set(df_m_filtrato["Deck_A"]).union(set(df_m_filtrato["Deck_B"]))))

                mat_vittorie = pd.DataFrame(0.0, index=mazzi, columns=mazzi)
                mat_totali = pd.DataFrame(0.0, index=mazzi, columns=mazzi)

                for _, row in df_m_filtrato.iterrows():
                    dA, dB = row["Deck_A"], row["Deck_B"]
                    wA, wB = row["W_A"], row["W_B"]
                    
                    mat_vittorie.loc[dA, dB] += wA
                    mat_vittorie.loc[dB, dA] += wB
                    
                    tot_games = wA + wB
                    mat_totali.loc[dA, dB] += tot_games
                    mat_totali.loc[dB, dA] += tot_games

                mat_winrate = (mat_vittorie / mat_totali * 100).round(1)

                if len(mazzi) > 0:
                    st.subheader(f"📊 Heatmap Win Rate % (Season: {season_m_sel} | Tappa: {tappa_m_sel})")
                    st.caption("I valori indicano la % di vittoria del mazzo sulla **riga (verticale)** contro il mazzo sulla **colonna (orizzontale)**.")

                    fig_heatmap = px.imshow(
                        mat_winrate,
                        labels=dict(x="Mazzo Avversario", y="Mazzo Giocato", color="Win Rate (%)"),
                        x=mazzi,
                        y=mazzi,
                        text_auto=True,
                        color_continuous_scale="RdYlGn",
                        range_color=[0, 100],
                        aspect="auto"
                    )
                    fig_heatmap.update_xaxes(side="top")
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    st.subheader("📋 Matrice Numerica Win Rate %")
                    st.dataframe(mat_winrate.fillna("-"), use_container_width=True)
                    
                    with st.expander("🔍 Mostra Volume Game Totali Giocati per Matchup"):
                        st.dataframe(mat_totali.astype(int), use_container_width=True)
                else:
                    st.warning("Nessun mazzo trovato per i filtri selezionati.")
            else:
                st.error("Assicurati che il foglio 'matchup' contenga le colonne: Deck_A, Deck_B, W_A, W_B.")
                
        except Exception as e_m:
            st.error(f"Errore durante l'elaborazione del foglio matchup: {e_m}")

except Exception as e:
    st.error(f"Errore generale durante il caricamento dei dati: {e}")