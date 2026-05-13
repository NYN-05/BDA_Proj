import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000";

interface Prediction {
  predicted_power: number;
  avg_power: number;
  date_hour: string;
  model: string;
  source: string;
  generated_at: string;
  id: string | null;
  mae: number | null;
  rmse: number | null;
  r2: number | null;
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[10px] text-white/40 uppercase tracking-widest">{label}</span>
      <span className="text-lg font-light text-white">{value}</span>
    </div>
  );
}

export default function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const loadPrediction = async () => {
    setError(null);
    setLoading(true);

    try {
      const predRes = await fetch(`${API_BASE}/predictions/latest`);
      if (!predRes.ok) {
        const err = await predRes.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `HTTP ${predRes.status}`);
      }
      setPrediction(await predRes.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploadError(null);
    setUploadSuccess(null);
    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const uploadRes = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) {
        const err = await uploadRes.json().catch(() => ({ message: "Unknown error" }));
        throw new Error(err.message || `HTTP ${uploadRes.status}`);
      }

      const result = await uploadRes.json();
      
      if (result.success) {
        setUploadSuccess(result.message);
        // Clear any previous error
        setError(null);
        // Load the new prediction
        await loadPrediction();
      } else {
        setUploadError(result.message || "Upload failed");
      }
    } catch (e: unknown) {
      setUploadError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  // Remove automatic loading on mount - now we wait for user upload
  // useEffect(() => {
  //   loadPrediction();
  // }, []);

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
              <p className="text-[10px] text-white/30 uppercase tracking-widest">
                {prediction?.model ? `${prediction.model} model` : "Model"}
              </p>
              <p className="text-[10px] text-white/30">v1.0</p>
            </div>
        </header>

        {!prediction ? (
          <section className="min-h-[60vh] flex flex-col justify-center">
            <div className="mb-8">
              <h2 className="text-3xl font-extralight tracking-tight mb-2">Upload Energy Data</h2>
              <p className="text-sm text-white/40 font-light">
                Upload a CSV or TXT file containing historical energy consumption data to generate predictions
              </p>
            </div>
            <div className="border border-dashed rounded-xl border-white/10 bg-white/[0.02]">
              <div className="py-16 flex flex-col items-center gap-5">
                <div className="flex flex-col items-center gap-4">
                  {/* File Upload Area */}
                  <div className="flex flex-col items-center gap-3 w-full max-w-xl">
                    <label className="cursor-pointer flex flex-col items-center justify-center w-full border-2 border-dashed border-white/20 rounded-lg p-6 hover:border-white/30 transition-all duration-200">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mb-3 h-6 w-6 text-white/60">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                      </svg>
                      <div className="flex flex-col items-center gap-1">
                        <p className="text-sm font-medium text-white/80">Drag & drop files here</p>
                        <p className="text-xs text-white/40">or click to select file</p>
                        <input
                          type="file"
                          accept=".csv,.txt"
                          className="hidden"
                          onChange={(e) => {
                            if (e.target.files && e.target.files[0]) {
                              handleFileUpload(e.target.files[0]);
                            }
                          }}
                        />
                      </div>
                    </label>
                    
                    {/* File Format Info */}
                    <div className="text-xs text-white/40 text-center">
                      <p>Supported formats: CSV or TXT files</p>
                      <p className="mt-1">Expected columns: Date, Time, Global_active_power, Global_reactive_power, Voltage, Global_intensity, Sub_metering_1, Sub_metering_2, Sub_metering_3</p>
                    </div>
                  </div>
                  
                  {uploadError && (
                    <div className="mt-4 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/20 w-full max-w-xl text-left">
                      <p className="text-sm text-red-400 font-light">{uploadError}</p>
                    </div>
                  )}
                  
                  {uploadSuccess && (
                    <div className="mt-4 px-4 py-3 rounded-lg bg-green-500/10 border border-green-500/20 w-full max-w-xl text-left">
                      <p className="text-sm text-green-400 font-light">{uploadSuccess}</p>
                    </div>
                  )}
                  
                  {uploading && (
                    <div className="flex flex-col items-center gap-4">
                      <div className="w-10 h-10 border border-white/10 border-t-white/60 rounded-full animate-spin" />
                      <span className="text-sm text-white/40 animate-pulse font-light tracking-wide">
                        Processing file&hellip;
                      </span>
                    </div>
                  )}
                </div>
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
                    {typeof prediction.predicted_power === 'number' ? prediction.predicted_power.toLocaleString() : '—'}
                  </p>
                  <p className="text-sm text-white/40 font-light mt-3">
                    kW &nbsp;&middot;&nbsp; Hour of {prediction.date_hour}
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
                  <StatCard label="MAE" value={typeof prediction.mae === 'number' ? prediction.mae.toFixed(2) : "—"} />
                  <StatCard label="RMSE" value={typeof prediction.rmse === 'number' ? prediction.rmse.toFixed(2) : "—"} />
                  <StatCard label="R²" value={typeof prediction.r2 === 'number' ? prediction.r2.toFixed(2) : "—"} />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
                <div>
                  <p className="text-sm text-white/60 font-light">Spark MLlib Forecast</p>
                  <p className="text-xs text-white/30 font-light">Source: {prediction.source}</p>
                </div>
              </div>
              <button
                onClick={loadPrediction}
                className="text-sm text-white/40 hover:text-white font-light border border-white/10 hover:border-white/30 px-5 py-2 rounded-lg transition-all duration-200"
                disabled={uploading}
              >
                {uploading ? "Processing..." : "Refresh Forecast"}
              </button>
            </div>
          </section>
        )}

        <footer className="mt-24 pt-8 border-t border-white/[0.05] flex items-center justify-between">
          <p className="text-[11px] text-white/20 font-light">
            Built with Spark MLlib &middot; FastAPI &middot; React
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