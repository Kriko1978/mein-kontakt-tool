import streamlit as st
import pandas as pd
from github import Github
import io
import re

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
def format_phone_number(phone):
    """Wandelt 0... in +49... um und sorgt dafür, dass das + bleibt."""
    if not phone:
        return ""
    # Nur Zahlen und das Plus behalten, alles andere (Leerzeichen, Klammern) weg
    phone = re.sub(r"[^\d+]", "", str(phone))
    
    # Wenn sie mit 0 beginnt (aber nicht 00), durch +49 ersetzen
    if phone.startswith("0") and not phone.startswith("00"):
        phone = "+49" + phone[1:]
    
    # Sicherstellen, dass ein + davor steht, falls es eine internationale Nummer ist
    if phone.startswith("49") and not phone.startswith("+"):
        phone = "+" + phone
        
    return phone

def load_data_from_github():
    spalten = ["Name", "Email", "Handy", "Büro", "Privat"]
    try:
        content = repo.get_contents(FILE_PATH)
        # dtype=str ist wichtig, damit das + am Anfang nicht gelöscht wird!
        df = pd.read_csv(io.StringIO(content.decoded_content.decode('utf-8')), dtype=str)
        for s in spalten:
            if s not in df.columns:
                df[s] = ""
        return df[spalten].fillna(""), content.sha
    except:
        return pd.DataFrame(columns=spalten), None

def save_to_github(df, sha, message="Update"):
    # Wir speichern explizit als String
    csv_string = df.to_csv(index=False, quoting=1) # quoting=1 setzt Anführungszeichen um Texte
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
        if row['Email']:
            vcard_content += f"EMAIL:{row['Email']}\n"
        
        # Telefonnummern
        if row['Handy']:
            vcard_content += f"TEL;TYPE=CELL:{row['Handy']}\n"
        if row['Büro']:
            vcard_content += f"TEL;TYPE=WORK:{row['Büro']}\n"
        if row['Privat']:
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
    st.write("📞 **Telefonnummern** (werden automatisch in +49 umgewandelt)")
    
    c1, c2, c3 = st.columns(3)
    num_handy = c1.text_input("Handy")
    num_buero = c2.text_input("Büro")
    num_privat = c3.text_input("Privat")

    if st.form_submit_button("Dauerhaft speichern"):
        if name:
            f_handy = format_phone_number(num_handy)
            f_buero = format_phone_number(num_buero)
            f_privat = format_phone_number(num_privat)
            
            new_entry = pd.DataFrame([{
                "Name": name, 
                "Email": email, 
                "Handy": f_handy,
                "Büro": f_buero,
                "Privat": f_privat
            }], dtype=str)
            
            updated_df = pd.concat([df, new_entry], ignore_index=True).astype(str)
            save_to_github(updated_df, file_sha, f"Hinzugefügt: {name}")
            st.success(f"✅ {name} gespeichert!")
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
        st.download_button("📲 iPhone Kontakte (vcf)", vcf_data, "Firma_Schuessler.vcf", "text/vcard")
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
            
            name_to_del = st.selectbox("Kontakt löschen", ["---"] + df["Name"].tolist())
            if name_to_del != "---" and st.button(f"{name_to_del} entfernen"):
                updated_df = df[df["Name"] != name_to_del]
                save_to_github(updated_df, file_sha, f"Gelöscht: {name_to_del}")
                st.rerun()
else:
    st.info("Liste ist leer.")
