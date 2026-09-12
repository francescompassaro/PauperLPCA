#!/bin/bash
echo "🧹 Pulizia modifiche locali non volute sul server..."
git checkout -- .

echo "⬇️ Scaricamento aggiornamenti da GitHub..."
git pull origin main

echo "📦 Verifica dipendenze..."
source venv/bin/activate
pip install -r requirements.txt

echo "🚀 Riavvio del servizio..."
sudo systemctl restart legapauper.service

echo "✅ Aggiornamento completato con successo!"
