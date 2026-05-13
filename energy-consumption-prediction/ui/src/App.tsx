import { useState, useRef, useCallback } from "react";

const API_BASE = "http://localhost:8000";

interface Prediction {
  predicted_kwh: number;
  month_start: string;
}

interface MonthlyPoint {
  month: string;
  actual: number;
  predicted: number;
}

interface Backtest {
  mae: number;
  rmse: number;
  r2: number;
  monthly: MonthlyPoint[];
}

function LineGraph({ data }: { data: MonthlyPoint[] }) { return null; }

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] text-white/40 uppercase tracking-widest">{label}</span>
      <span className="text-lg font-light text-white">{value}</span>
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [backtest, setBacktest] = useState<Backtest | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (f: File) => {
    setFile(f);
    setError(null);
    setPrediction(null);
    setBacktest(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", f);

      const [predRes, btRes] = await Promise.all([
        fetch(`${API_BASE}/predict`, { method: "POST", body: formData }),
        fetch(`${API_BASE}/backtest`, { method: "POST", body: formData }),
      ]);

      if (!predRes.ok) {
        const err = await predRes.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `HTTP ${predRes.status}`);
      }

      setPrediction(await predRes.json());
      if (btRes.ok) setBacktest(await btRes.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  return (
    <div className="min-h-screen bg-[#070710] text-white font-light">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <header className="mb-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#070710" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
              </svg>
            </div>
            <div>
              <p className="text-[11px] text-white/30 uppercase tracking-[0.25em]">BDA Project</p>
              <h1 className="text-xl font-normal tracking-tight text-white">Energy Consumption Forecast</h1>
            </div>
          </div>
            <div className="text-right">
              <p className="text-[10px] text-white/30 uppercase tracking-widest">XGBoost Model</p>
              <p className="text-[10px] text-white/30">v1.0</p>
            </div>
        </header>

        {!prediction ? (
          <section className="min-h-[60vh] flex flex-col justify-center">
            <div className="mb-8">
              <h2 className="text-3xl font-extralight tracking-tight mb-2">Upload Dataset</h2>
              <p className="text-sm text-white/40 font-light">
                Drop your household power consumption file or browse to upload.
              </p>
            </div>

            <div
              className={[
                "border border-dashed rounded-xl transition-all duration-300 cursor-pointer group",
                dragOver
                  ? "border-white bg-white/5"
                  : "border-white/10 hover:border-white/30 bg-white/[0.02] hover:bg-white/[0.04]",
              ].join(" ")}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => inputRef.current?.click()}
            >
              <input
                ref={inputRef}
                type="file"
                accept=".txt,.csv"
                className="hidden"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
              />
              <div className="py-20 flex flex-col items-center gap-5 pointer-events-none">
                {loading ? (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-10 h-10 border border-white/10 border-t-white/60 rounded-full animate-spin" />
                    <span className="text-sm text-white/40 animate-pulse font-light tracking-wide">
                      Processing data&hellip;
                    </span>
                  </div>
                ) : (
                  <>
                    <div className="w-14 h-14 rounded-full border border-white/10 flex items-center justify-center group-hover:border-white/20 transition-colors">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <p className="text-sm text-white/60 font-light">Drop file here or click to browse</p>
                      <p className="text-xs text-white/25 font-light mt-1">Supports .txt and .csv formats</p>
                    </div>
                  </>
                )}
              </div>
            </div>

            {error && (
              <div className="mt-4 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20">
                <p className="text-sm text-red-400 font-light">{error}</p>
              </div>
            )}
          </section>
        ) : (
          <section className="space-y-10 animate-[fadeIn_0.5s_ease]">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="space-y-6 p-8 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                <div className="flex items-center justify-between">
                  <p className="text-[11px] text-white/40 uppercase tracking-[0.2em]">Next Month Prediction</p>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] text-emerald-400/80 uppercase tracking-widest">
                    Forecast
                  </span>
                </div>
                <div>
                  <p className="text-7xl font-extralight tracking-tighter text-white leading-none">
                    {prediction.predicted_kwh.toLocaleString()}
                  </p>
                  <p className="text-sm text-white/40 font-light mt-3">
                    kWh &nbsp;&middot;&nbsp; Month of {prediction.month_start}
                  </p>
                </div>
              </div>

              <div className="space-y-6 p-8 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                <div className="flex items-center justify-between">
                  <p className="text-[11px] text-white/40 uppercase tracking-[0.2em]">Model Metrics</p>
                  <span className="px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] text-blue-400/80 uppercase tracking-widest">
                    Accuracy
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-6">
                  <StatCard label="MAE" value={backtest?.mae.toFixed(2) ?? "—"} />
                  <StatCard label="RMSE" value={backtest?.rmse.toFixed(2) ?? "—"} />
                  <StatCard label="R²" value={backtest?.r2.toFixed(4) ?? "—"} />
                </div>
              </div>
            </div>

            {backtest && backtest.monthly.length > 0 && (
              <div className="p-8 rounded-2xl bg-white/[0.03] border border-white/[0.06]">
                <p className="text-[11px] text-white/40 uppercase tracking-[0.2em] mb-6">
                  Monthly Breakdown &mdash; Last {Math.min(12, backtest.monthly.length)} Months
                </p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm font-light">
                    <thead>
                      <tr className="border-b border-white/[0.06]">
                        <th className="text-left text-[10px] text-white/30 uppercase tracking-widest pb-3 font-normal">Month</th>
                        <th className="text-right text-[10px] text-white/30 uppercase tracking-widest pb-3 font-normal">Actual (kWh)</th>
                        <th className="text-right text-[10px] text-white/30 uppercase tracking-widest pb-3 font-normal">Predicted</th>
                        <th className="text-right text-[10px] text-white/30 uppercase tracking-widest pb-3 font-normal">Variance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {backtest.monthly.slice(-12).map((d, i) => {
                        const variance = d.actual - d.predicted;
                        const pct = ((variance / d.actual) * 100).toFixed(1);
                        return (
                          <tr key={i} className="border-b border-white/[0.04] last:border-0">
                            <td className="py-2.5 text-white/60">{d.month.slice(0, 7)}</td>
                            <td className="py-2.5 text-right text-white">{d.actual.toFixed(4)}</td>
                            <td className="py-2.5 text-right text-white/50">{d.predicted.toFixed(4)}</td>
                            <td className={`py-2.5 text-right ${variance >= 0 ? "text-lime-400/70" : "text-red-400/70"}`}>
                              {variance >= 0 ? "+" : ""}{variance.toFixed(4)} ({pct}%)
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {file && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                  <div>
                    <p className="text-sm text-white/60 font-light">{file.name}</p>
                    <p className="text-xs text-white/30 font-light">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button
                  onClick={() => { setPrediction(null); setBacktest(null); setFile(null); setError(null); }}
                  className="text-sm text-white/40 hover:text-white font-light border border-white/10 hover:border-white/30 px-5 py-2 rounded-lg transition-all duration-200"
                >
                  Upload New File
                </button>
              </div>
            )}
          </section>
        )}

        <footer className="mt-24 pt-8 border-t border-white/[0.05] flex items-center justify-between">
          <p className="text-[11px] text-white/20 font-light">
            Built with scikit-learn &middot; FastAPI &middot; React
          </p>
          <p className="text-[11px] text-white/20 font-light">Big Data Analytics Project</p>
        </footer>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
