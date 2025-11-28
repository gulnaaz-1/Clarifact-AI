"use client"
import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, Shield, Activity, Globe, Search, 
  BarChart2, FileText, X, Check, MapPin, ExternalLink,
  Menu, Bell, ChevronRight
} from 'lucide-react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, 
  AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid 
} from 'recharts';

// --- MOCK DATA FOR PREVIEW (Fallback if backend is offline) ---
const MOCK_FEED = [
  {
    id: 1,
    title: "BREAKING: 'Miracle Cure' for Aging Found in Backyard Weeds",
    summary: "A viral post claims common dandelions can reverse aging by 20 years. Experts warn of toxicity.",
    risk_score: 0.89,
    source: "ViralHealth.net",
    geo: "USA",
    image: "https://images.unsplash.com/photo-1507208773393-40d9fc9f600e?auto=format&fit=crop&q=80&w=600",
    trend: "up"
  },
  {
    id: 2,
    title: "Election Officials Confirm New Voting Protocols",
    summary: "Standard press release detailing extended hours for upcoming regional elections.",
    risk_score: 0.12,
    source: "City Gazette",
    geo: "UK",
    image: "https://images.unsplash.com/photo-1540910419868-4749459ca6dc?auto=format&fit=crop&q=80&w=600",
    trend: "stable"
  },
  {
    id: 3,
    title: "Leaked Documents Prove Earth is Hollow",
    summary: "Conspiracy theorists circulate doctored NASA images claiming a subterranean civilization.",
    risk_score: 0.95,
    source: "DeepTruths Forum",
    geo: "RUS",
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=600",
    trend: "up"
  }
];

const MOCK_CHART_DATA = [
  { name: '00:00', risk: 20 }, { name: '04:00', risk: 35 },
  { name: '08:00', risk: 50 }, { name: '12:00', risk: 85 },
  { name: '16:00', risk: 60 }, { name: '20:00', risk: 40 },
  { name: '23:59', risk: 30 },
];

const COLORS = ['#10B981', '#F59E0B', '#EF4444', '#7F1D1D'];

const API_URL = "http://localhost:8000"; // Assuming backend runs locally

// --- COMPONENT: RISK METER ---
const RiskMeter = ({ score }) => {
  const data = [
    { name: 'Risk', value: score },
    { name: 'Safe', value: 1 - score }
  ];
  
  let color = COLORS[0]; // Green
  let label = "LOW";
  if (score > 0.3) { color = COLORS[1]; label = "MEDIUM"; }
  if (score > 0.6) { color = COLORS[2]; label = "HIGH"; }
  if (score > 0.8) { color = COLORS[3]; label = "CRITICAL"; }

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-slate-900 rounded-xl border border-slate-700">
      <div className="relative w-32 h-32">
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              innerRadius={35}
              outerRadius={50}
              startAngle={180}
              endAngle={0}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              <Cell fill={color} />
              <Cell fill="#334155" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute top-16 left-0 right-0 text-center">
          <span className="text-2xl font-bold text-white">{(score * 100).toFixed(0)}%</span>
        </div>
      </div>
      <span className="text-sm font-semibold tracking-wider mt-[-10px]" style={{ color }}>{label} RISK</span>
    </div>
  );
};

// --- COMPONENT: NAV BAR ---
const Navbar = ({ activeTab, setActiveTab }) => (
  <nav className="h-16 border-b border-slate-800 bg-slate-950 flex items-center px-6 sticky top-0 z-50 justify-between">
    <div className="flex items-center gap-2">
      <Activity className="text-red-500 w-6 h-6" />
      <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-500 to-orange-400">
      Clarifact<span className="text-slate-500 font-light">AI</span>
      </span>
    </div>
    
    <div className="hidden md:flex gap-8">
      {['dashboard', 'analyze', 'feed'].map((tab) => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={`capitalize text-sm font-medium transition-colors ${
            activeTab === tab ? 'text-white' : 'text-slate-500 hover:text-slate-300'
          }`}
        >
          {tab}
        </button>
      ))}
    </div>

    <div className="flex items-center gap-4">
      <Bell className="w-5 h-5 text-slate-400 hover:text-white cursor-pointer" />
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold text-white">
        A
      </div>
    </div>
  </nav>
);

// --- COMPONENT: ANALYZE PAGE ---
const AnalyzePage = () => {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [models, setModels] = useState(null);

  useEffect(() => {
    // Fetch models info on mount
    fetch(`${API_URL}/models`)
      .then(res => res.json())
      .then(data => setModels(data))
      .catch(() => console.log("Could not fetch models info"));
  }, []);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      // Try fetching from real backend
      const res = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input })
      });
      if (!res.ok) throw new Error("Backend offline");
      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.warn("Using mock analysis data");
      // Fallback Mock Data
      setTimeout(() => {
        setResult({
          risk_score: 0.85,
          risk_level: "CRITICAL",
          components: {
            fake_news_score: 0.9,
            contradiction_score: 0.4,
            sensationalism_score: 0.8,
            source_credibility: 0.2,
            virality_score: 0.95
          },
          claims: [
            "Entity X is secretly controlling the weather.",
            "Government admitted to hiding aliens in 1995."
          ],
          evidence: [
            "Wikipedia (Meteorology): Weather modification is strictly regulated...",
            "Wikipedia (Roswell): The 1947 incident was identified as a balloon..."
          ],
          geolocation: "Unknown",
          reasoning: "The text contains high levels of emotive language and unsubstantiated claims that contradict established consensus.",
          models_used: {
            fake_news_detection: "jy46604790/Fake-News-Bert-Detect",
            sentiment_analysis: "cardiffnlp/twitter-roberta-base-sentiment",
            nli_contradiction: "roberta-large-mnli"
          }
        });
        setLoading(false);
      }, 1500);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <h2 className="text-2xl font-bold text-white mb-2">Deep Content Inspector</h2>
        <p className="text-slate-400 mb-6">Paste article text, URL, or social post to detect harmful patterns using our ensemble of ML models.</p>
        
        <div className="relative">
          <textarea 
            className="w-full bg-slate-950 border border-slate-700 rounded-xl p-4 text-slate-200 focus:ring-2 focus:ring-blue-500 focus:outline-none min-h-[150px]"
            placeholder="Paste suspicious content here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button 
            onClick={handleAnalyze}
            disabled={loading || !input}
            className="absolute bottom-4 right-4 bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? <Activity className="animate-spin w-4 h-4" /> : <Search className="w-4 h-4" />}
            Analyze
          </button>
        </div>

        {/* Models Info Box */}
        {models && (
          <div className="mt-6 p-4 bg-slate-950 border border-slate-700 rounded-lg">
            <p className="text-xs text-slate-500 font-semibold uppercase mb-3">Active ML Models</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(models.models || {}).map(([key, model]) => (
                <div key={key} className="text-xs">
                  <p className="text-slate-400 font-medium capitalize">{key.replace(/_/g, ' ')}</p>
                  <p className="text-blue-400 truncate text-[10px] mt-1">{model}</p>
                </div>
              ))}
            </div>
            <p className="text-[10px] text-slate-600 mt-3">Mode: {models.mode || 'PRODUCTION'}</p>
          </div>
        )}
      </div>

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* Main Score Card */}
          <div className="md:col-span-1">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 h-full flex flex-col items-center">
              <h3 className="text-slate-400 font-medium mb-4">Overall Threat Level</h3>
              <RiskMeter score={result.risk_score} />
              <div className="mt-6 w-full space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Sensationalism</span>
                  <span className="text-yellow-400 text-xs font-mono">{(result.components?.sensationalism_score * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Fake News Score</span>
                  <span className="text-red-400 text-xs font-mono">{(result.components?.fake_news_score * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Source Credibility</span>
                  <span className="text-green-400 text-xs font-mono">{(result.components?.source_credibility * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Contradiction Risk</span>
                  <span className="text-orange-400 text-xs font-mono">{(result.components?.contradiction_score * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Details & Claims */}
          <div className="md:col-span-2 space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-blue-500" /> Model Reasoning
              </h3>
              <p className="text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-lg border border-slate-800">
                {result.reasoning}
              </p>
              
              {/* Models Used */}
              {result.models_used && (
                <div className="mt-4 p-3 bg-slate-950 border border-slate-700 rounded-lg">
                  <p className="text-xs text-slate-500 font-semibold uppercase mb-2">Models Used</p>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(result.models_used).map(([key, model]) => (
                      <div key={key} className="text-xs bg-slate-900 p-2 rounded border border-slate-700">
                        <p className="text-slate-400 font-medium capitalize">{key.replace(/_/g, ' ')}</p>
                        <p className="text-blue-300 truncate text-[9px] mt-1">{model}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-500" /> Extracted Claims
              </h3>
              <div className="space-y-3">
                {result.claims.map((claim, idx) => (
                  <div key={idx} className="flex gap-3 items-start group">
                    <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center text-xs text-slate-400 flex-shrink-0 group-hover:bg-slate-700">
                      {idx + 1}
                    </div>
                    <div>
                      <p className="text-slate-200 text-sm">{claim}</p>
                      {result.evidence[idx] && (
                         <p className="text-xs text-slate-500 mt-1 pl-2 border-l-2 border-slate-700">
                           Checking: {result.evidence[idx]}
                         </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// --- COMPONENT: DASHBOARD & FEED ---
const Dashboard = () => {
  const [feed, setFeed] = useState(MOCK_FEED);
  const [heatmap, setHeatmap] = useState(null);
  const [heatmapLoading, setHeatmapLoading] = useState(false);

  useEffect(() => {
    // Attempt real fetch
    fetch(`${API_URL}/feed`)
      .then(res => res.json())
      .then(data => setFeed(data))
      .catch(() => console.log("Using mock feed"));

    // Fetch heatmap data
    setHeatmapLoading(true);
    fetch(`${API_URL}/heatmap`)
      .then(res => res.json())
      .then(data => {
        // Convert object to array for display
        const heatmapArray = Object.entries(data || {}).map(([country, risk]) => ({
          country,
          risk: typeof risk === 'number' ? risk : 0
        })).sort((a, b) => b.risk - a.risk);
        setHeatmap(heatmapArray);
        setHeatmapLoading(false);
      })
      .catch(() => {
        console.log("Using mock heatmap");
        setHeatmap([
          { country: 'USA', risk: 0.65 },
          { country: 'India', risk: 0.58 },
          { country: 'Russia', risk: 0.72 },
          { country: 'Brazil', risk: 0.42 }
        ]);
        setHeatmapLoading(false);
      });
  }, []);

  const getRiskColor = (risk) => {
    if (risk > 0.8) return 'from-red-600 to-red-500';
    if (risk > 0.6) return 'from-orange-600 to-orange-500';
    if (risk > 0.4) return 'from-yellow-600 to-yellow-500';
    return 'from-green-600 to-green-500';
  };

  const getRiskLabel = (risk) => {
    if (risk > 0.8) return 'CRITICAL';
    if (risk > 0.6) return 'HIGH';
    if (risk > 0.4) return 'MEDIUM';
    return 'LOW';
  };

  return (
    <div className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      {/* LEFT: Live Map & Stats */}
      <div className="lg:col-span-8 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
            <div className="text-slate-400 text-xs font-semibold uppercase">Active Threats</div>
            <div className="text-3xl font-bold text-white mt-1">1,240</div>
            <div className="text-green-500 text-xs flex items-center mt-2">
              <Activity className="w-3 h-3 mr-1" /> +12% from yesterday
            </div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
             <div className="text-slate-400 text-xs font-semibold uppercase">Top Source</div>
             <div className="text-3xl font-bold text-white mt-1">X (Twitter)</div>
             <div className="text-red-500 text-xs flex items-center mt-2">
              High Velocity
            </div>
          </div>
          <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
             <div className="text-slate-400 text-xs font-semibold uppercase">Blocked</div>
             <div className="text-3xl font-bold text-white mt-1">85</div>
             <div className="text-slate-500 text-xs flex items-center mt-2">
              Auto-moderated
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 min-h-[300px]">
          <h3 className="text-white font-bold mb-6">Viral Spike Velocity (24h)</h3>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={MOCK_CHART_DATA}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area type="monotone" dataKey="risk" stroke="#EF4444" fillOpacity={1} fill="url(#colorRisk)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Global Heatmap - Real Data */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 min-h-[320px]">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-white font-bold flex items-center gap-2">
              <Globe className="w-5 h-5 text-blue-400" /> Geographic Risk Distribution
            </h3>
            {heatmapLoading && <Activity className="animate-spin w-4 h-4 text-slate-400" />}
          </div>

          {heatmap && heatmap.length > 0 ? (
            <div className="space-y-3">
              {heatmap.map((item, idx) => (
                <div key={item.country} className="group">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-300 w-20">{item.country}</span>
                    <div className="flex items-center gap-3 flex-1">
                      <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r ${getRiskColor(item.risk)} transition-all duration-300 group-hover:shadow-lg group-hover:shadow-red-500/50`}
                          style={{ width: `${Math.max(item.risk * 100, 5)}%` }}
                        />
                      </div>
                      <div className="text-right">
                        <span className={`text-xs font-bold px-2 py-1 rounded ${
                          item.risk > 0.8 ? 'bg-red-500/20 text-red-400' :
                          item.risk > 0.6 ? 'bg-orange-500/20 text-orange-400' :
                          item.risk > 0.4 ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-green-500/20 text-green-400'
                        }`}>
                          {getRiskLabel(item.risk)}
                        </span>
                        <p className="text-xs text-slate-500 mt-1">{(item.risk * 100).toFixed(1)}%</p>
                      </div>
                    </div>
                  </div>
                  <div className="h-px bg-slate-800/50"></div>
                </div>
              ))}

              {/* Summary Stats */}
              <div className="mt-6 p-4 bg-slate-950 rounded-lg border border-slate-700">
                <p className="text-xs text-slate-500 font-semibold uppercase mb-3">Summary</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-slate-400 text-xs">Highest Risk</p>
                    <p className="text-lg font-bold text-red-400 mt-1">
                      {heatmap[0]?.country} ({(heatmap[0]?.risk * 100).toFixed(0)}%)
                    </p>
                  </div>
                  <div>
                    <p className="text-slate-400 text-xs">Monitored Regions</p>
                    <p className="text-lg font-bold text-blue-400 mt-1">{heatmap.length}</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[200px] text-slate-600">
              <Globe className="w-24 h-24 opacity-20 animate-pulse" />
            </div>
          )}
        </div>
      </div>

      {/* RIGHT: Feed */}
      <div className="lg:col-span-4 space-y-4">
        <h3 className="text-lg font-bold text-white mb-2">Live Risk Feed</h3>
        <div className="space-y-4 overflow-y-auto max-h-[800px] pr-2 scrollbar-thin scrollbar-thumb-slate-700">
          {feed.map((news) => (
            <div key={news.id} className="bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-slate-600 transition-colors group cursor-pointer">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    news.risk_score > 0.7 ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'
                  }`}>
                    {news.risk_score > 0.7 ? 'High Risk' : 'Safe'}
                  </span>
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <MapPin className="w-3 h-3" /> {news.geo || news.geolocation}
                  </span>
                </div>
                <span className="text-xs text-slate-500">{news.timestamp || 'Just now'}</span>
              </div>
              
              <div className="flex gap-3 mb-3">
                 <img src={news.image || news.image_url} alt="thumb" className="w-16 h-16 rounded-lg object-cover bg-slate-800" />
                 <h4 className="text-sm font-medium text-slate-200 line-clamp-3 group-hover:text-blue-400 transition-colors">
                   {news.title}
                 </h4>
              </div>

              <div className="flex justify-between items-center border-t border-slate-800 pt-3 mt-2">
                <div>
                  <span className="text-xs text-slate-500 font-medium">{news.source}</span>
                  {news.confidence && <p className="text-[10px] text-slate-600 mt-1">Confidence: {(news.confidence * 100).toFixed(0)}%</p>}
                </div>
                <button className="text-xs text-blue-500 hover:text-blue-400 flex items-center gap-1">
                  Details <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

// --- MAIN LAYOUT ---
export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-blue-500 selection:text-white">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="animate-in fade-in duration-500">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'analyze' && <AnalyzePage />}
        {activeTab === 'feed' && <Dashboard />} {/* Reusing Dashboard for Feed for simplicity */}
      </main>
    </div>
  );
}