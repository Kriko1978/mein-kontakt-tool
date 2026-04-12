import streamlit as st
import pandas as pd
from github import Github
import io

# Seite einrichten
st.set_page_config(page_title="Kontakt-Tresor Cloud", page_icon="🔐")

# --- KONFIGURATION ---
# Stell sicher, dass GITHUB_TOKEN in den Streamlit Secrets hinterlegt ist!
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "Kriko1978/mein-kontakt-tool" 
FILE_PATH = "kontakte.csv"

# Verbindung zu GitHub herstellen
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# --- FUNKTIONEN ---
def load_data_from_github():
    try:
        content = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(content.decoded_content.decode('utf-8')))
        return df, content.sha
    except:
        # Falls Datei nicht existiert, leeres Datenblatt erstellen
        columns = ["Title", "URL", "Username", "Password", "Notes"]
        return pd.DataFrame(columns=columns), None

def save_to_github(df, sha):
    csv_string = df.to_csv(index=False)
    if sha:
        repo.update_file(FILE_PATH, "Update Kontakte", csv_string, sha)
    else:
        repo.create_file(FILE_PATH, "Initialer Export", csv_string)

# --- HAUPTTEIL ---
st.title("🔐 Mein Kontakt-Manager (GitHub Cloud)")

# Daten laden
df, file_sha = load_data_from_github()

# Eingabe-Formular
with st.form("kontakt_form", clear_on_submit=True):
    st.subheader("Neuen Kontakt hinzufügen")
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail Adresse")
    
    st.write("---")
    st.write("📞 **Telefonnummern**")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        typ1 = st.selectbox("Typ 1", ["Handy", "Privat", "Büro"], key="t1")
    with col2:
        num1 = st.text_input("Nummer 1", placeholder="z.B. 0170...")

    col3, col4 = st.columns([1, 2])
    with col3:
        typ2 = st.selectbox("Typ 2", ["Büro", "Handy", "Privat"], key="t2")
    with col4:
        num2 = st.text_input("Nummer 2", placeholder="z.B. 030...")

    if st.form_submit_button("Für immer speichern"):
        if name:
            # Notizen mit Nummern zusammenbauen
            notes_list = []
            if num1: notes_list.append(f"{typ1}: {num1}")
            if num2: notes_list.append(f"{typ2}: {num2}")
            full_notes = " | ".join(notes_list)
            
            # Neue Zeile erstellen
            new_entry = pd.DataFrame([{
                "Title": name,
                "URL": "",
                "Username": email,
                "Password": "",
                "Notes": full_notes
            }])
            
            # Daten zusammenführen und bei GitHub speichern
            updated_df = pd.concat([df, new_entry], ignore_index=True)
            save_to_github(updated_df, file_sha)
            
            st.success(f"✅ {name} wurde dauerhaft gespeichert!")
            st.rerun()
        else:
            st.error("Bitte gib mindestens einen Namen ein.")

st.divider()

# Tabelle anzeigen
st.subheader("Gespeicherte Kontakte")
if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # Export-Button für Apple
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 CSV für Apple herunterladen",
        data=csv,
        file_name="kontakte_export.csv",
        mime="text/csv",
    )
else:
    st.info("Noch keine Kontakte in der Cloud gespeichert.")
