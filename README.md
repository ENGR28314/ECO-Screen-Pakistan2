# 🌍 EcoScreen Pakistan
## Pakistan Climate & Environmental Decision-Support Platform

EcoScreen Pakistan is a Streamlit prototype for early-stage climate-risk screening and climate-resilient development planning.

### Core question
> **What climate risks could affect this development, and what should we investigate next?**

### Hazards screened
- 🌊 Flooding
- 🌡️ Extreme heat
- 🌧️ Extreme precipitation
- 💧 Drought
- ⛰️ Landslides
- 🔥 Wildfire
- 🌪️ Storms
- 🌊 Sea-level rise

### Pakistan geographic coverage
Provinces/territories:
- Punjab
- Sindh
- Khyber Pakhtunkhwa
- Balochistan
- Islamabad Capital Territory
- Gilgit-Baltistan
- Azad Jammu & Kashmir

Mountain/geographic systems:
- Himalayas
- Karakoram
- Hindu Kush
- Sulaiman / Koh-e-Suleman
- Spīn Ghar / Safed Koh
- Kirthar
- Salt Range

### Climate-resilient infrastructure priorities
The screening highlights issues that may need additional attention, including:
- drainage and flood protection
- heat resilience
- water availability
- slope stability
- asset protection
- emergency preparedness
- operational continuity
- climate-adaptive design

### Features
- Climate/disaster risk scoring: Low → Moderate → High → Critical
- Illustrative temperature and precipitation simulations
- Project-level CHRI proxy
- GHG accounting
- Illustrative shadow carbon calculation
- Climate co-benefit score
- Sector in-depth screening
- Groq-powered AI screening explanation
- CSV export of project screening inputs

### Groq API key
You **must create your own Groq API key**. The developer cannot provide a private API key for your account.

The app is configured for `openai/gpt-oss-120b`, a currently supported Groq production model. See Groq's current model list before deployment.

For Streamlit Community Cloud:
1. Open your app in Streamlit Community Cloud.
2. Open **Settings / Secrets**.
3. Add:

```toml
GROQ_API_KEY = "your-real-key"
```

Do not put the key in `app.py`, `workflow.py`, GitHub, or `requirements.txt`.

### Local setup
```bash
python -m venv .venv
```

Windows:
```bash
.venv\\Scripts\\activate
```

Install:
```bash
pip install -r requirements.txt
```

Run:
```bash
streamlit run app.py
```

### GitHub + Streamlit Community Cloud
1. Create a GitHub repository, for example `ecoscreen-pakistan`.
2. Upload all files from this folder.
3. In Streamlit Community Cloud, create a new app.
4. Select the GitHub repository and branch.
5. Set main file to `app.py`.
6. Add `GROQ_API_KEY` in Streamlit Secrets.
7. Deploy.

### Important scope
This is an early-stage decision-support prototype. It does not replace EIA/IEE, engineering design, hydrological or geotechnical studies, health assessment, disaster-risk assessment, regulatory review, or official climate forecasts. Simulation values are illustrative unless replaced with verified datasets and documented methods.

The CHRI component is explicitly a project-level proxy and does not reproduce the official World Bank CHRI methodology.

### Architecture
```text
User
  ↓
Streamlit UI
  ↓
Project + geography inputs
  ↓
Risk scoring engine
  ↓
Regional / mountain-system resilience priorities
  ↓
GHG + CHRI proxy + co-benefits
  ↓
Groq AI explanation
  ↓
Dashboard + CSV export
```

### Future production upgrades
Replace illustrative simulations with validated CCKP, PMD, ERA5, CHIRPS, CMIP6 and/or verified national datasets as legally and technically appropriate. Add data provenance, dates, uncertainty, geospatial layers, validated sector indicators, and documented emission/carbon methodologies.
