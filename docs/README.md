# FLL Tournament Scheduler - Web Interface

## Setup

### 1. Activeer GitHub Pages
1. Ga naar je GitHub repository settings
2. Scroll naar "Pages"
3. Selecteer "Deploy from a branch"
4. Kies branch: **main** en folder: **/docs**
5. Klik "Save"

Je website is dan beschikbaar op: `https://koenvanwijk.github.io/ffl-schedule/`

### 2. Maak een GitHub Personal Access Token
De web interface heeft een token nodig om workflows te triggeren:

1. Ga naar GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Klik "Generate new token (classic)"
3. Geef het een naam zoals "FLL Scheduler Web"
4. Selecteer de volgende scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Klik "Generate token"
6. **Kopieer de token** (je ziet hem maar 1x!)

### 3. Gebruik de Web Interface
1. Open de website
2. Bij eerste gebruik: voer je GitHub token in
3. Vul de toernooi configuratie in
4. Klik "Genereer Schema"
5. Wacht 2-5 minuten terwijl de scheduler draait
6. Download het gegenereerde schema

## Security Note
Je GitHub token wordt opgeslagen in localStorage in je browser. Deze is alleen zichtbaar voor jou. Deel je token nooit met anderen!

## Hoe het werkt
1. **Frontend** (docs/index.html) - Form voor configuratie
2. **JavaScript** (docs/scheduler.js) - Triggert GitHub Actions via API
3. **GitHub Actions** (.github/workflows/schedule.yml) - Draait Python scheduler
4. **Artifact** - Gegenereerd schema wordt gedownload

## Troubleshooting

**"401 Unauthorized"**
- Je token is ongeldig of verlopen
- Maak een nieuw token aan
- Clear localStorage en refresh de pagina

**"Workflow niet gestart"**
- Check of `workflow_dispatch` is ingeschakeld in de workflow file
- Controleer of je token de juiste permissions heeft

**"Schema niet gegenereerd"**
- Check GitHub Actions logs voor errors
- Probeer met minder teams of meer tijdsloten
