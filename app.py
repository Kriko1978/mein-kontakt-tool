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
        return pd.DataFrame(columns=["Title", "Username", "Notes"]), None

def save_to_github(df, sha, message="Update"):
    csv_string = df.to_csv(index=False)
    if sha:
        repo.update_file(FILE_PATH, message, csv_string, sha)
    else:
        repo.create_file(FILE_PATH, "Initial", csv_string)

def create_vcard(df):
    vcard_content = ""
    for _, row in df.iterrows():
        vcard_content += "BEGIN:VCARD\n"
        vcard_content += "VERSION:3.0\n"
        vcard_content += f"FN:{row['Title']}\n"  # Full Name
        if pd.notnull(row['Username']) and row['Username'] != "":
            vcard_content += f"EMAIL:{row['Username']}\n"
        
        # Telefonnummern aus den Notes extrahieren
        if pd.notnull(row['Notes']):
            notes = row['Notes'].split(" | ")
            for note in notes:
                if ":" in note:
                    typ, num = note.split(":", 1)
                    vcard_content += f"TEL;TYPE={typ.strip().upper()}:{num.strip()}\n"
        
        vcard_content += "END:VCARD\n"
    return vcard_content

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
    t1 = c1.selectbox("Typ 1", ["HANDY", "WORK", "HOME"], key="t1")
    n1 = c2.text_input("Nummer 1", key="n1")
    
    c3, c4 = st.columns([1, 2])
    t2 = c3.selectbox("Typ 2", ["WORK", "HANDY", "HOME"], key="t2")
    n2 = c4.text_input("Nummer 2", key="n2")
    
    c5, c6 = st.columns([1, 2])
    t3 = c5.selectbox("Typ 3", ["HOME", "HANDY", "WORK"], key="t3")
    n3 = c6.text_input("Nummer 3", key="n3")

    if st.form_submit_button("Dauerhaft speichern"):
        if name:
            phones = []
            if n1: phones.append(f"{t1}: {n1}")
            if n2: phones.append(f"{t2}: {n2}")
            if n3: phones.append(f"{t3}: {n3}")
            full_notes = " | ".join(phones)
            
            new_entry = pd.DataFrame([{"Title": name, "Username": email, "Notes": full_notes}])
            updated_df = pd.concat([df, new_entry], ignore_index=True)
            save_to_github(updated_df, file_sha, f"Hinzugefügt: {name}")
            st.success("✅ Gespeichert!")
            st.rerun()

st.divider()

# --- ANZEIGE ---
st.subheader("📁 Kontakte Firma Schüßler")
st.dataframe(df, use_container_width=True)

if not df.empty:
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        # vCard Export (Das Beste fürs iPhone)
        vcf_data = create_vcard(df)
        st.download_button(
            label="📲 iPhone Kontakte (vcf)",
            data=vcf_data,
            file_name="Firma_Schuessler.vcf",
            mime="text/vcard"
        )
    
    with col_dl2:
        # CSV Export (Backup)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Backup (csv)", csv, "kontakte.csv", "text/csv")
    
    # --- LÖSCH-BEREICH ---
    st.write("---")
    with st.expander("⚠️ Admin Bereich"):
        pw = st.text_input("Passwort", type="password")
        if pw == "erkenschwick":
            if st.button("🚨 ALLES LÖSCHEN"):
                save_to_github(pd.DataFrame(columns=["Title", "Username", "Notes"]), file_sha, "Geleert")
                st.rerun()
else:
    st.info("Liste ist leer.")
