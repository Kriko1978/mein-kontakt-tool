import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Seite konfigurieren
st.set_page_config(page_title="Kontakt-Cloud", page_icon="🔐")

st.title("🔐 Mein Kontakt-Manager (Cloud)")

# Verbindung zu Google Sheets definieren
conn = st.connection("gsheets", type=GSheetsConnection)

# Daten aus der Cloud laden (ttl=0 damit es sofort aktualisiert)
try:
    df = conn.read(ttl=0)
except:
    df = pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])

# Eingabe-Formular
with st.form("new_contact", clear_on_submit=True):
    st.subheader("Neuen Eintrag erstellen")
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail Adresse")
    phone = st.text_input("Telefonnummer")
    
    if st.form_submit_button("Direkt in Cloud speichern"):
        if name:
            # Neue Zeile vorbereiten
            new_data = pd.DataFrame([{
                "Title": name,
                "URL": "",
                "Username": email,
                "Password": "",
                "Notes": phone
            }])
            # Bestehende Daten mit neuen kombinieren
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # DER MAGISCHE BEFEHL: Schreibt direkt in die Google Tabelle
            conn.update(data=updated_df)
            
            st.success(f"✅ {name} wurde in Google Sheets gespeichert!")
            st.rerun()
        else:
            st.error("Bitte einen Namen eingeben!")

st.divider()

# Anzeige der Cloud-Daten
st.subheader("Deine gespeicherten Kontakte")
if not df.empty:
    # Nur Zeilen anzeigen, die nicht komplett leer sind
    st.dataframe(df.dropna(how="all"), use_container_width=True)
    
    # Export-Button für Apple
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 CSV für Apple herunterladen", csv, "kontakte.csv", "text/csv")
else:
    st.info("Noch keine Daten in der Cloud gefunden.")
