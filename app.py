import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kontakt Cloud", page_icon="🔐")

# HIER DEINEN LINK EINTRAGEN (der mit /export?format=csv am Ende)
SHEET_URL = "DEIN_LINK_ZUM_EXPORT_CSV"

st.title("🔐 Mein Kontakt-Tresor")

# Funktion zum Laden der Daten
def load_data():
    try:
        # Erlaubt das Lesen direkt aus der Google Tabelle
        return pd.read_csv(SHEET_URL)
    except:
        return pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])

df = load_data()

# Eingabe-Maske
with st.form("add_form", clear_on_submit=True):
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail")
    phone = st.text_input("Telefon")
    submitted = st.form_submit_button("Hinzufügen")
    
    if submitted and name:
        st.success(f"{name} wurde lokal hinzugefügt. Kopiere die CSV unten, um deine Google Tabelle manuell zu füllen, oder nutze den Download!")
        # Hier fügen wir es dem aktuellen DF hinzu
        new_line = pd.DataFrame([{"Title": name, "URL": "", "Username": email, "Password": "", "Notes": phone}])
        df = pd.concat([df, new_line], ignore_index=True)

# Tabelle anzeigen
st.dataframe(df, use_container_width=True)

# Export-Bereich
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 CSV Datei herunterladen", data=csv, file_name="kontakte.csv")
