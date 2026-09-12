Avvio
pip -m install requirements.txt

source venv/bin/activate

git init branch -M main

git remote add origin https://github.com/francescompassaro/PauperLPCA.git

git push -u origin main

streamlit app.py



