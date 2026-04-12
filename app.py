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
    spalten = ["Name", "Email", "Handy", "Büro", "Privat"]
    try:
        content = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(content.decoded_content.decode('utf-8')))
        # Sicherstellen, dass alle Spalten existieren
        for s in spalten:
            if s not in df.columns:
                df[s] = ""
        return df[spalten], content.sha
    except:
        return pd.DataFrame(columns=spalten), None

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
        vcard_content += f"FN:{row['Name']}\n"
        if pd.notnull(row['Email']) and str(row['Email']).strip() != "":
            vcard_content += f"EMAIL:{row['Email']}\n"
        
        # Telefonnummern einzeln zuordnen
        if pd.notnull(row['Handy']) and str(row['Handy']).strip() != "":
            vcard_content += f"TEL;TYPE=CELL:{row['Handy']}\n"
        if pd.notnull(row['Büro']) and str(row['Büro']).strip() != "":
            vcard_content += f"TEL;TYPE=WORK:{row['Büro']}\n"
        if pd.notnull(row['Privat']) and str(row['Privat']).strip() != "":
            vcard_content += f"TEL;TYPE=HOME:{row['Privat']}\n"
        
        vcard_content += "END:VCARD\n"
    return vcard_content

# --- DATEN LADEN ---
df, file_sha = load_data_from_github()

st.title("🔐 Kontakt-Manager")

# --- EINGABE-FORMULAR ---
with st.form("kontakt_form", clear_on_submit=True):
    st.subheader("Neuen Kontakt hinzufügen")
    name = st.text_input("Name / Firma")
    email = st.text_input("E-Mail Adresse")
    
    st.write("---")
    st.write("📞 **Telefonnummern**")
    
    c1, c2, c3 = st.columns(3)
    num_handy = c1.text_input("Handy", placeholder="0170...")
    num_buero = c2.text_input("Büro", placeholder="030...")
    num_privat = c3.text_input("Privat", placeholder="0123...")

    if st.form_submit_button("Dauerhaft speichern"):
        if name:
            new_entry = pd.DataFrame([{
                "Name": name, 
                "Email": email, 
                "Handy": num_handy,
                "Büro": num_buero,
                "Privat": num_privat
            }])
            
            updated_df = pd.concat([df, new_entry], ignore_index=True)
            save_to_github(updated_df, file_sha, f"Hinzugefügt: {name}")
            st.success(f"✅ {name} wurde gespeichert!")
            st.rerun()
        else:
            st.error("Bitte einen Namen eingeben!")

st.divider()

# --- ANZEIGE DER LISTE ---
st.subheader("📁 Kontakte Firma Schüßler")
st.dataframe(df, use_container_width=True)

if not df.empty:
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        vcf_data = create_vcard(df)
        st.download_button(
            label="📲 iPhone Kontakte (vcf)",
            data=vcf_data,
            file_name="Firma_Schuessler.vcf",
            mime="text/vcard"
        )
    with col_dl2:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Backup (csv)", csv, "kontakte.csv", "text/csv")
    
    st.write("---")
    with st.expander("⚠️ Admin Bereich"):
        pw = st.text_input("Passwort", type="password")
        if pw == "erkenschwick":
            if st.button("🚨 ALLES LÖSCHEN"):
                save_to_github(pd.DataFrame(columns=["Name", "Email", "Handy", "Büro", "Privat"]), file_sha, "Geleert")
                st.rerun()
            
            st.write("Einzelnen Kontakt löschen:")
            name_to_del = st.selectbox("Kontakt wählen", ["---"] + df["Name"].tolist())
            if name_to_del != "---" and st.button(f"{name_to_del} löschen"):
                updated_df = df[df["Name"] != name_to_del]
                save_to_github(updated_df, file_sha, f"Gelöscht: {name_to_del}")
                st.rerun()
else:
    st.info("Liste ist leer.")
