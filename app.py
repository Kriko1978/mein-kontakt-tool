import streamlit as st
import pandas as pd
from github import Github
import io
import re

# --- SEITE EINRICHTEN ---
st.set_page_config(page_title="Kontakt-Tresor Firma Schüßler", page_icon="🔐", layout="wide")

# --- KONFIGURATION & GITHUB CONNECTION ---
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "Kriko1978/mein-kontakt-tool" 
    FILE_PATH = "kontakte.csv"
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except Exception as e:
    st.error("Konfiguration fehlerhaft! Bitte GITHUB_TOKEN in den Secrets prüfen.")
    st.stop()

# --- FUNKTIONEN ---
def format_phone_number(phone):
    """Bereinigt Nummern und formatiert sie einheitlich auf +49."""
    if not phone or pd.isna(phone):
        return ""
    # Nur Ziffern extrahieren
    digits = re.sub(r"\D", "", str(phone))
    if not digits:
        return ""
    
    # 0049... zu 49...
    if digits.startswith("00"):
        digits = digits[2:]
    # 0... zu 49...
    elif digits.startswith("0"):
        digits = "49" + digits[1:]
    
    # Sicherstellen, dass ein + davor steht
    return "+" + digits if not digits.startswith("+") else digits

def load_data_from_github():
    spalten = ["Name", "Email", "Handy", "Büro", "Privat"]
    try:
        content = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(content.decoded_content.decode('utf-8')), dtype=str)
        for s in spalten:
            if s not in df.columns:
                df[s] = ""
        return df[spalten].fillna("").astype(str), content.sha
    except:
        return pd.DataFrame(columns=spalten), None

def save_to_github(df, sha, message="Update"):
    # Sortieren nach Name für bessere Übersicht
    df = df.sort_values(by="Name")
    csv_string = df.to_csv(index=False, quoting=1)
    if sha:
        repo.update_file(FILE_PATH, message, csv_string, sha)
    else:
        repo.create_file(FILE_PATH, "Initial", csv_string)

def create_vcard(df):
    vcard_content = ""
    for _, row in df.iterrows():
        vcard_content += "BEGIN:VCARD\nVERSION:3.0\n"
        vcard_content += f"FN:{row['Name']}\n"
        if row['Email']: vcard_content += f"EMAIL:{row['Email']}\n"
        if row['Handy']: vcard_content += f"TEL;TYPE=CELL:{row['Handy']}\n"
        if row['Büro']:  vcard_content += f"TEL;TYPE=WORK:{row['Büro']}\n"
        if row['Privat']: vcard_content += f"TEL;TYPE=HOME:{row['Privat']}\n"
        vcard_content += "END:VCARD\n"
    return vcard_content

# --- DATEN LADEN ---
df, file_sha = load_data_from_github()

st.title("🔐 Kontakt-Manager Firma Schüßler")

# --- TABS ERSTELLEN ---
tab_view, tab_add, tab_edit, tab_admin = st.tabs([
    "📂 Kontakte ansehen", 
    "➕ Neu anlegen", 
    "📝 Bearbeiten", 
    "⚠️ Admin"
])

# --- TAB 1: ANSEHEN & SUCHE ---
with tab_view:
    search = st.text_input("🔍 Suche nach Name oder Firma")
    display_df = df.copy()
    if search:
        display_df = display_df[display_df["Name"].str.contains(search, case=False, na=False)]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            vcf_data = create_vcard(df)
            st.download_button("📲 Alle als vCard (iPhone/Outlook)", vcf_data, "Kontakte_Schuessler.vcf", "text/vcard")
        with col2:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV Backup", csv_data, "kontakte_backup.csv", "text/csv")

# --- TAB 2: NEU ANLEGEN ---
with tab_add:
    with st.form("add_form", clear_on_submit=True):
        st.subheader("Neuen Kontakt hinzufügen")
        name = st.text_input("Name / Firma")
        email = st.text_input("E-Mail")
        c1, c2, c3 = st.columns(3)
        h = c1.text_input("Handy")
        b = c2.text_input("Büro")
        p = c3.text_input("Privat")
        
        if st.form_submit_button("Dauerhaft speichern"):
            if name:
                new_entry = pd.DataFrame([{
                    "Name": name, "Email": email, 
                    "Handy": format_phone_number(h), 
                    "Büro": format_phone_number(b), 
                    "Privat": format_phone_number(p)
                }], dtype=str)
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                save_to_github(updated_df, file_sha, f"Neu: {name}")
                st.success(f"✅ {name} wurde hinzugefügt!")
                st.rerun()
            else:
                st.error("Name ist ein Pflichtfeld!")

# --- TAB 3: BEARBEITEN ---
with tab_edit:
    if not df.empty:
        contact_to_edit = st.selectbox("Kontakt zum Bearbeiten auswählen", ["---"] + sorted(df["Name"].tolist()))
        
        if contact_to_edit != "---":
            current_data = df[df["Name"] == contact_to_edit].iloc[0]
            
            with st.form("edit_form"):
                e_name = st.text_input("Name / Firma", value=current_data["Name"])
                e_email = st.text_input("E-Mail", value=current_data["Email"])
                c1, c2, c3 = st.columns(3)
                e_h = c1.text_input("Handy", value=current_data["Handy"])
                e_b = c2.text_input("Büro", value=current_data["Büro"])
                e_p = c3.text_input("Privat", value=current_data["Privat"])
                
                if st.form_submit_button("Änderungen speichern"):
                    # Alten Eintrag entfernen, neuen hinzufügen
                    updated_df = df[df["Name"] != contact_to_edit].copy()
                    new_entry = pd.DataFrame([{
                        "Name": e_name, "Email": e_email, 
                        "Handy": format_phone_number(e_h), 
                        "Büro": format_phone_number(e_b), 
                        "Privat": format_phone_number(e_p)
                    }], dtype=str)
                    updated_df = pd.concat([updated_df, new_entry], ignore_index=True)
                    save_to_github(updated_df, file_sha, f"Update: {e_name}")
                    st.success(f"✅ {e_name} wurde aktualisiert!")
                    st.rerun()
    else:
        st.info("Keine Kontakte vorhanden.")

# --- TAB 4: ADMIN (LÖSCHEN) ---
with tab_admin:
    st.subheader("Gefahrenbereich")
    pw = st.text_input("Admin-Passwort", type="password")
    
    if pw == "erkenschwick":
        st.warning("Achtung: Löschvorgänge können nicht rückgängig gemacht werden.")
        
        # Einzelnen Kontakt löschen
        del_name = st.selectbox("Kontakt endgültig löschen", ["---"] + sorted(df["Name"].tolist()))
        if del_name != "---":
            if st.button(f"❌ {del_name} jetzt löschen"):
                updated_df = df[df["Name"] != del_name]
                save_to_github(updated_df, file_sha, f"Gelöscht: {del_name}")
                st.success(f"{del_name} wurde entfernt.")
                st.rerun()
        
        st.divider()
        # Alles löschen
        if st.button("🚨 GESAMTE DATENBANK LEEREN"):
            save_to_github(pd.DataFrame(columns=["Name", "Email", "Handy", "Büro", "Privat"]), file_sha, "Datenbank geleert")
            st.rerun()
