import streamlit as st
import pandas as pd
from github import Github
import io

# Seite einrichten
st.set_page_config(page_title="Kontakt-Tresor Cloud", page_icon="🔐")

# --- KONFIGURATION (GitHub Weg) ---
# Wichtig: GITHUB_TOKEN muss in den Streamlit Secrets stehen!
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "Kriko1978/mein-kontakt-tool" 
    FILE_PATH = "kontakte.csv"

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except:
    st.error("Konfiguration fehlt! Bitte GITHUB_TOKEN in den Secrets hinterlegen.")
    st.stop()

# --- FUNKTIONEN ---
def load_data_from_github():
    try:
        content = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(content.decoded_content.decode('utf-8')))
        return df, content.sha
    except:
        columns = ["Title", "URL", "Username", "Password", "Notes"]
        return pd.DataFrame(columns=columns), None

def save_to_github(df, sha):
    csv_string = df.to_csv(index=False)
    if sha:
        repo.update_file(FILE_PATH, "Update Kontakte", csv_string, sha)
    else:
        repo.create_file(FILE_PATH, "Initialer Export", csv_string)

# --- HAUPTTEIL ---
st.title("🔐 Mein Kontakt-Manager")

# Daten laden
df, file_sha = load_data_from_github()

with st.form("kontakt_form", clear_on_submit=True):
    st.subheader("Neuen Kontakt hinzufügen")
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail Adresse")
    
    st.write("---")
    st.write("📞 **Telefonnummern**")
    
    # Erste Nummer
    col1, col2 = st.columns([1, 2])
    with col1:
        typ1 = st.selectbox("Typ 1", ["Handy", "Privat", "Büro"], key="t1")
    with col2:
        num1 = st.text_input("Nummer 1", placeholder="z.B. 0170...")

    # Zweite Nummer
    col3, col4 = st.columns([1, 2])
    with col3:
        typ2 = st.selectbox("Typ 2", ["Büro", "Handy", "Privat"], key="t2")
    with col4:
        num2 = st.text_input("Nummer 2", placeholder="z.B. 030...")

    if st.form_submit_button("Dauerhaft speichern"):
        if name:
            # Nummern für das Notiz-Feld aufbereiten
            parts = []
            if num1: parts.append(f"{typ1}: {num1}")
            if num2: parts.append(f"{typ2}: {num2}")
            full_notes = " | ".join(parts)
            
            new_entry = pd.DataFrame([{
                "Title": name,
                "URL": "",
                "Username": email,
                "Password": "",
                "Notes": full_notes
            }])
            
            updated_df = pd.concat([df, new_entry], ignore_index=True)
            save_to_github(updated_df, file_sha)
            
            st.success(f"✅ {name} mit {len(parts)} Nummer(n) gespeichert!")
            st.rerun()
        else:
            st.error("Bitte gib einen Namen ein.")

st.divider()

#
