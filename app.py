import streamlit as st
import pandas as pd

# Seite einrichten
st.set_page_config(page_title="Kontakt-Tresor", page_icon="🔐")

st.title("🔐 Mein Kontakt-Manager")

# Initialisiere den Speicher im Browser-Sitzungsspeicher
if 'contacts' not in st.session_state:
    st.session_state.contacts = pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])

# Eingabe-Formular
with st.form("kontakt_form", clear_on_submit=True):
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail")
    phone = st.text_input("Telefonnummer")
    
    if st.form_submit_button("Hinzufügen"):
        if name:
            new_entry = pd.DataFrame([{
                "Title": name,
                "URL": "",
                "Username": email,
                "Password": "",
                "Notes": phone
            }])
            st.session_state.contacts = pd.concat([st.session_state.contacts, new_entry], ignore_index=True)
            st.success(f"{name} hinzugefügt!")
        else:
            st.warning("Bitte Namen eingeben.")

# Anzeige der Tabelle
st.subheader("Deine Liste")
if not st.session_state.contacts.empty:
    # Tabelle anzeigen
    st.dataframe(st.session_state.contacts, use_container_width=True)
    
    # Der wichtigste Teil: Der Export
    csv = st.session_state.contacts.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 CSV für Apple herunterladen",
        data=csv,
        file_name="kontakte_export.csv",
        mime="text/csv",
    )
    
    if st.button("Liste leeren"):
        st.session_state.contacts = pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])
        st.rerun()
else:
    st.info("Noch keine Kontakte gespeichert.")

st.info("Tipp: Lade die CSV regelmäßig herunter, um deine Daten lokal zu sichern!")
