import streamlit as st
import pandas as pd
from github import Github
import io

# Seite einrichten
st.set_page_config(page_title="Kontakt-Tresor Firma Schüßler", page_icon="🔐")

# --- KONFIGURATION ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "Kriko1978/mein-kontakt-tool" 
    FILE_PATH = "kontakte.csv"

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except Exception as e:
    st.error("Konfiguration fehlerhaft! Prüfe deine Secrets.")
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

def save_to_github(df, sha, message="Update"):
    csv_string = df.to_csv(index=False)
    if sha:
        repo.update_file(FILE_PATH, message, csv_string, sha)
    else:
        repo.create_file(FILE_PATH, "Initial", csv_string)

# --- DATEN LADEN ---
df, file_sha = load_data_from_github()

st.title("🔐 Kontakt-Manager")

# --- EINGABE-FORMULAR ---
with st.form("kontakt_form", clear_on_submit=True):
    st.subheader("Neuen Kontakt hinzufügen")
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail")
    
    st.write("---")
    st.write("📞 **Telefonnummern**")
    c1, c2 = st.columns([1, 2])
    t1 = c1.selectbox("Typ 1", ["Handy", "Privat", "Büro"])
    n1 = c2.text_input("Nummer 1")
    
    c3, c4 = st.columns([1, 2])
    t2 = c3.selectbox("Typ 2", ["Büro", "Handy", "Privat"])
    n2 = c4.text_input("Nummer 2")

    if st.form_submit_button("Dauerhaft speichern"):
        if name:
            notes = f"{t1}: {n1}"
            if n2: notes += f" | {t2}: {n2}"
            
            new_entry = pd.DataFrame([{"Title": name, "URL": "", "Username": email, "Password": "", "Notes": notes}])
            updated_df = pd.concat([df, new_entry], ignore_index=True)
            
            save_to_github(updated_df, file_sha, f"Hinzugefügt: {name}")
            st.success(f"✅ {name} gespeichert!")
            st.rerun()

st.divider()

# --- ANZEIGE DER LISTE ---
st.subheader("📁 Kontakte Firma Schüßler")
st.dataframe(df, use_container_width=True)

if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 CSV für Apple herunterladen", csv, "kontakte.csv", "text/csv")
    
    # --- LÖSCH-BEREICH MIT PASSWORT ---
    st.write("---")
    with st.expander("⚠️ Kontakte löschen (Admin Bereich)"):
        pw_input = st.text_input("Sicherheits-Passwort eingeben", type="password")
        
        if pw_input == "erkenschwick":
            st.warning("Achtung: Du kannst jetzt die gesamte Liste leeren oder einzelne Einträge entfernen.")
            
            # Button für alles löschen
            if st.button("🚨 GESAMTE LISTE LÖSCHEN"):
                empty_df = pd.DataFrame(columns=["Title", "URL", "Username", "Password", "Notes"])
                save_to_github(empty_df, file_sha, "Liste komplett geleert")
                st.success("Die Liste wurde vollständig gelöscht.")
                st.rerun()
                
            # Einzelne Zeile löschen
            st.write("Einzelnen Kontakt löschen:")
            name_to_delete = st.selectbox("Welchen Kontakt entfernen?", ["---"] + df["Title"].tolist())
            if name_to_delete != "---":
                if st.button(f"'{name_to_delete}' endgültig löschen"):
                    updated_df = df[df["Title"] != name_to_delete]
                    save_to_github(updated_df, file_sha, f"Gelöscht: {name_to_delete}")
                    st.success(f"{name_to_delete} wurde entfernt.")
                    st.rerun()
        elif pw_input != "":
            st.error("Falsches Passwort!")
else:
    st.info("Die Liste ist aktuell noch leer.")
