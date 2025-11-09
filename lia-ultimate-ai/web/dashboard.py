from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import psutil

app = FastAPI(title="LIA Monitoring Dashboard")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
        <head>
            <title>LIA Ultimate AI - Monitoring</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>🧠 LIA Ultimate AI - Dashboard Temps Réel</h1>
            <div id="metrics">
                <div>📊 Tweets collectés: <span id="tweetCount">0</span></div>
                <div>📹 Vidéos YouTube: <span id="youtubeCount">0</span></div>
                <div>💾 Mémoire utilisée: <span id="memoryUsage">0</span>%</div>
                <div>⚡ CPU: <span id="cpuUsage">0</span>%</div>
            </div>
            <div id="charts"></div>
            <script>
                // Code JavaScript pour métriques temps réel
                setInterval(async () => {
                    const response = await fetch('/api/metrics');
                    const data = await response.json();
                    document.getElementById('tweetCount').textContent = data.tweets_collected;
                    document.getElementById('youtubeCount').textContent = data.youtube_videos;
                    document.getElementById('memoryUsage').textContent = data.memory_usage;
                    document.getElementById('cpuUsage').textContent = data.cpu_usage;
                }, 2000);
            </script>
        </body>
    </html>
    """


@app.get("/api/metrics")
async def get_metrics():
    return {
        "tweets_collected": 0,
        "youtube_videos": 0,
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "status": "operational",
    }
