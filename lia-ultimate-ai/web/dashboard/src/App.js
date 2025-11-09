import React, { useEffect, useState } from 'react';

const API_BASE =
  import.meta.env.VITE_API_URL ??
  process.env.REACT_APP_API_URL ??
  'http://localhost:8000';

function App() {
  const [metrics, setMetrics] = useState({});
  const [trendingData, setTrendingData] = useState({});
  const [token, setToken] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/generate-token`);
        if (!res.ok) {
          throw new Error(`Token request failed: ${res.status}`);
        }
        const data = await res.json();
        setToken(data.token);
      } catch (err) {
        console.error('Token fetch error', err);
        setError('Impossible de récupérer le token du dashboard.');
      }
    };
    fetchToken();
  }, []);

  useEffect(() => {
    if (!token) return;

    let isCancelled = false;

    const fetchData = async () => {
      try {
        const [metricsRes, trendingRes] = await Promise.all([
          fetch(`${API_BASE}/api/v1/dashboard/metrics`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          fetch(`${API_BASE}/api/v1/data/trending?platform=all&limit=5`, {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        if (!metricsRes.ok || !trendingRes.ok) {
          throw new Error(
            `API error: metrics ${metricsRes.status} / trending ${trendingRes.status}`
          );
        }

        const [metricsJson, trendingJson] = await Promise.all([
          metricsRes.json(),
          trendingRes.json()
        ]);

        if (!isCancelled) {
          setMetrics(metricsJson);
          setTrendingData(trendingJson);
          setError(null);
        }
      } catch (err) {
        console.error('Erreur fetch:', err);
        if (!isCancelled) {
          setError('Erreur lors de la récupération des données temps réel.');
        }
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);

    return () => {
      isCancelled = true;
      clearInterval(interval);
    };
  }, [token]);

  const tweetsCollected = metrics.system?.tweets_collected ?? 0;
  const youtubeVideos = metrics.system?.youtube_videos ?? 0;
  const redditPosts = metrics.system?.reddit_posts ?? 0;
  const cpuPercent = metrics.realtime?.cpu_percent ?? 0;
  const status = metrics.status ?? 'loading...';

  return (
    <div className="App">
      <header className="dashboard-header">
        <h1>🧠 LIA ULTIMATE AI - DASHBOARD ENTERPRISE</h1>
        <div className="status-indicators">
          <span className={`status ${status === 'operational' ? 'online' : 'offline'}`}>
            ● {status}
          </span>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>📊 Données Collectées</h3>
          <div className="metric-value">{tweetsCollected}</div>
          <div className="metric-label">Tweets</div>
        </div>

        <div className="metric-card">
          <h3>📹 Contenu YouTube</h3>
          <div className="metric-value">{youtubeVideos}</div>
          <div className="metric-label">Vidéos</div>
        </div>

        <div className="metric-card">
          <h3>📝 Discussions Reddit</h3>
          <div className="metric-value">{redditPosts}</div>
          <div className="metric-label">Posts</div>
        </div>

        <div className="metric-card">
          <h3>⚡ Performance</h3>
          <div className="metric-value">{cpuPercent}%</div>
          <div className="metric-label">CPU</div>
        </div>
      </div>

      <div className="realtime-data">
        <h2>📈 Données Temps Réel</h2>

        <div className="platform-sections">
          <div className="platform-section">
            <h3>🐦 Derniers Tweets</h3>
            {(trendingData.twitter ?? []).map((tweet) => (
              <div key={tweet._id} className="data-item">
                <p>{tweet.text}</p>
                <small>
                  {tweet.collected_at
                    ? new Date(tweet.collected_at).toLocaleTimeString()
                    : ''}
                </small>
              </div>
            ))}
          </div>

          <div className="platform-section">
            <h3>📹 Vidéos Tendances</h3>
            {(trendingData.youtube ?? []).map((video) => (
              <div key={video._id} className="data-item">
                <p>{video.title}</p>
                <small>
                  {video.channel_title} •{' '}
                  {video.statistics?.viewCount
                    ? Number(video.statistics.viewCount).toLocaleString()
                    : 0}{' '}
                  vues
                </small>
              </div>
            ))}
          </div>

          <div className="platform-section">
            <h3>📝 Posts Populaires</h3>
            {(trendingData.reddit ?? []).map((post) => (
              <div key={post._id} className="data-item">
                <p>{post.title}</p>
                <small>
                  r/{post.subreddit} • {post.score} points
                </small>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
