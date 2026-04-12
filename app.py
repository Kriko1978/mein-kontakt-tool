import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Kontakt Tresor Cloud", page_icon="🔐")

st.title("🔐 Kontakt-Manager (Cloud-Speicher)")

# Verbindung zu Google Sheets herstellen
conn = st.connection("gsheets", type=GSheetsConnection)

# Daten aus Google Sheets laden
df = conn.read(ttl="0") # ttl=0 sorgt dafür, dass die Daten immer frisch geladen werden

# Eingabe-Maske
with st.expander("➕ Neuen Kontakt hinzufügen", expanded=True):
    with st.form("contact_form", clear_on_submit=True):
        name = st.text_input("Name / Firma")
        email = st.text_input("E-Mail Adresse")
        col1, col2 = st.columns(2)
        with col1:
            typ = st.selectbox("Typ", ["Privat", "Geschäftlich", "Mobil"])
        with col2:
            phone = st.text_input("Telefonnummer")
        
        submitted = st.form_submit_button("Hinzufügen & Speichern")
        
        if submitted and name:
            new_row = pd.DataFrame([{
                "Title": name,
                "URL": "",
                "Username": email,
                "Password": "",
                "Notes": f"Typ: {typ} | Tel: {phone}"
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"{name} wurde in der Cloud gespeichert!")
            st.rerun()

# Anzeige der Liste
st.subheader("Deine Kontakte (aus der Cloud)")
if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # CSV Export für Apple Schlüssel-App
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Als CSV für Apple exportieren", data=csv, file_name="kontakte.csv", mime="text/csv")
else:
    st.info("Noch keine Kontakte gespeichert.")
