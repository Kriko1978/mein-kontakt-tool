import streamlit as st
import pandas as pd

# Seite einrichten
st.set_page_config(page_title="Kontakt-Tresor", page_icon="🔐")

st.title("🔐 Mein Kontakt-Manager")

# Initialisiere den Speicher
if 'contacts' not in st.session_state:
    st.session_state.contacts = pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])

# Eingabe-Formular
with st.form("kontakt_form", clear_on_submit=True):
    st.subheader("Neuen Kontakt mit mehreren Nummern")
    
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail Adresse")
    
    st.write("---")
    st.write("📞 **Telefonnummern**")
    
    # Erste Nummer
    col1, col2 = st.columns([1, 2])
    with col1:
        typ1 = st.selectbox("Typ 1", ["Privat", "Büro", "Handy"], key="t1")
    with col2:
        num1 = st.text_input("Nummer 1", placeholder="0170...")

    # Zweite Nummer
    col3, col4 = st.columns([1, 2])
    with col3:
        typ2 = st.selectbox("Typ 2", ["Handy", "Büro", "Privat"], key="t2")
    with col4:
        num2 = st.text_input("Nummer 2", placeholder="030...")

    submitted = st.form_submit_button("Kontakt hinzufügen")
    
    if submitted and name:
        # Wir fassen die Nummern für das Notiz-Feld zusammen
        phone_notes = f"{typ1}: {num1}"
        if num2: # Nur hinzufügen, wenn eine zweite Nummer eingetragen wurde
            phone_notes += f" | {typ2}: {num2}"
            
        new_entry = pd.DataFrame([{
            "Title": name,
            "URL": "",
            "Username": email,
            "Password": "",
            "Notes": phone_notes
        }])
        
        st.session_state.contacts = pd.concat([st.session_state.contacts, new_entry], ignore_index=True)
        st.success(f"✅ {name} mit Nummern gespeichert!")
    elif submitted:
        st.warning("Bitte gib mindestens einen Namen ein.")

# Anzeige der Tabelle
st.subheader("Deine Liste")
if not st.session_state.contacts.empty:
    st.dataframe(st.session_state.contacts, use_container_width=True)
    
    # Export-Button
    csv = st.session_state.contacts.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 CSV für Apple herunterladen",
        data=csv,
        file_name="kontakte_export.csv",
        mime="text/csv",
    )
    
    if st.button("Gesamte Liste leeren"):
        st.session_state.contacts = pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])
        st.rerun()
else:
    st.info("Noch keine Kontakte in dieser Sitzung gespeichert.")
