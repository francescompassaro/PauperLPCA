

Avvio
## INSTALLAZIONE AMBIENTE VIRTUALE
python -m venv venv
### ATTIVARE L'AMBIENTE VIRTUALE
source venv/bin/activate


## STEP PER CARICARE LA PRIMA VOLTA IL PROGETTO SU  GIT
git init
git add .
git init
git branch -M main
git remote add origin https://github.com/francescompassaro/PauperLPCA.git
git push -u origin main

## CARICARE LE MODIFICHE AL REPOSITORI REMOTO
git add .
git push -u origin main

# SE VOGLIO SCARICARE AGGIORNAMENTI 
git pull

se da errore:
git checkout --nomefile.estensione ripristica il file allo stato originale del repository
e poi rifare il pull


## INSTALLAZIONE PROGETTO
### SCARICA PROGETTO 
git clone https://github.com/francescompassaro/PauperLPCA.git
### INSTALLA LIBRERIE
pip install -r requirements.txt
### AVVIA L'APPLICAZIONE
streamlit app.py

