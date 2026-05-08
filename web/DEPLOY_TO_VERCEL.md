# Deploying BIG_LOG to Vercel

This is a **Web Deployment Layer** for your project. This allows anyone to view your IoT Pipeline and Dashboard live on the web without needing to install Hadoop or Docker.

## How to Deploy (Step-by-Step)

### 1. Push the new `web/` folder to GitHub
If you haven't already, push your current project to a GitHub repository.
```bash
git add web/
git commit -m "Add web deployment layer"
git push origin main
```

### 2. Connect to Vercel
1. Go to [Vercel.com](https://vercel.com) and log in (Free).
2. Click **"Add New..."** -> **"Project"**.
3. Import your **BIG_LOG** repository.
4. **IMPORTANT: Settings before Deploying:**
   - **Root Directory**: Select the `web` folder.
   - **Framework Preset**: Other.
   - **Build Command**: (Leave Empty).
   - **Output Directory**: (Leave Empty).
5. Click **Deploy**.

### 3. Done!
The project will be live at `https://your-project-name.vercel.app`.

---

## What I Built for You
*   **`web/app.py`**: A unified version of your project that runs the **Streaming Simulator**, the **MapReduce Logic**, and the **Dashboard UI** all in one place.
*   **`web/index.html`**: Uses **Stlite** to run Python directly in the browser (Serverless).
*   **`web/data_sample.csv`**: A 5,000-row sample of your data to power the live demonstration.

## Why this is great
- **Zero Cost**: Completely free on Vercel's hobby tier.
- **High Fidelity**: It uses your actual `ERROR` detection and `MapReduce` aggregation logic.
