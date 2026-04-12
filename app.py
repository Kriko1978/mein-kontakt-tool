import streamlit as st
import pandas as pd

st.set_page_config(page_title="Kontakt Tresor", page_icon="🔐")

st.title("🔐 Kontakt-Manager (CSV)")

# Datenbank-Simulation (Wir nutzen Session State für die aktuelle Sitzung)
if 'contacts' not in st.session_state:
    st.session_state.contacts = pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])

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
        
        submitted = st.form_submit_button("Hinzufügen")
        
        if submitted and name:
            new_data = {
                "Title": name,
                "URL": "",
                "Username": email,
                "Password": "",
                "Notes": f"Typ: {typ} | Tel: {phone}"
            }
            st.session_state.contacts = pd.concat([st.session_state.contacts, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"{name} hinzugefügt!")

# Anzeige der Liste
st.subheader("Deine Kontakte")
if not st.session_state.contacts.empty:
    # Tabelle anzeigen
    edited_df = st.data_editor(st.session_state.contacts, num_rows="dynamic", use_container_width=True)
    st.session_state.contacts = edited_df

    # CSV Export
    csv = st.session_state.contacts.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Gesamte Liste als CSV herunterladen",
        data=csv,
        file_name="kontakte_export.csv",
        mime="text/csv",
    )
else:
    st.info("Noch keine Kontakte in der Liste.")

# Hinweis zur Speicherung
st.warning("Hinweis: Ohne Datenbank-Anbindung werden die Daten beim Neustart der App zurückgesetzt.")
