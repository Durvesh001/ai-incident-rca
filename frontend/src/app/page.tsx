"use client";

import { useState } from "react";

type AnalyzeResponse = {
  extracted_fields: {
    service: string | null;
    severity: string | null;
    error_type: string;
    metric: string | null;
  };
  similar_incidents: {
    score: number;
    incident: {
      id: string;
      title: string;
      service: string;
      severity: string;
      root_cause: string;
      remediation: string[];
    };
  }[];
  relevant_runbooks: {
    score: number;
    runbook: {
      id: string;
      alert: string;
      service: string;
      description: string;
      diagnosis_steps: string[];
      remediation_steps: string[];
    };
  }[];
  rca: {
    incident_summary: string;
    impact: string;
    evidence: string[];
    probable_root_cause: string;
    suggested_remediation: string[];
    confidence_score: number;
  };
};

const sampleAlert = `Service: payment-service
Severity: P1
Error: timeout while calling checkout-service
Metric: 5xx error rate increased to 18%`;

export default function Home() {
  const [alertText, setAlertText] = useState(sampleAlert);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeIncident() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          alert_text: alertText,
        }),   
      });

      if (!response.ok) {
        throw new Error("Failed to analyze incident");
      }

      const data = await response.json();
      setResult(data);
    } catch {
      setError("Could not connect to backend. Make sure FastAPI is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-semibold">AI Incident RCA Assistant</h1>
          <p className="mt-2 text-slate-400">
            Evidence-backed incident analysis using historical incidents and runbooks.
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
          <section className="rounded-lg border border-slate-800 bg-slate-900 p-5">
            <h2 className="mb-3 text-lg font-medium">Incident Input</h2>

            <textarea
              value={alertText}
              onChange={(event) => setAlertText(event.target.value)}
              className="h-72 w-full resize-none rounded-md border border-slate-700 bg-slate-950 p-4 text-sm text-slate-100 outline-none focus:border-cyan-500"
              placeholder="Paste alert or log details here..."
            />

            <button
              onClick={analyzeIncident}
              disabled={loading || alertText.trim().length === 0}
              className="mt-4 w-full rounded-md bg-cyan-500 px-4 py-2 font-medium text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            >
              {loading ? "Analyzing..." : "Analyze Incident"}
            </button>

            {error && (
              <p className="mt-4 rounded-md border border-red-800 bg-red-950 p-3 text-sm text-red-200">
                {error}
              </p>
            )}
          </section>

          <section className="space-y-6">
            {!result && (
              <div className="rounded-lg border border-slate-800 bg-slate-900 p-6 text-slate-400">
                RCA output will appear here after analysis.
              </div>
            )}

            {result && (
              <>
                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h2 className="text-xl font-semibold">RCA Draft</h2>
                      <p className="mt-2 text-slate-300">{result.rca.incident_summary}</p>
                    </div>

                    <div className="rounded-md bg-cyan-500 px-3 py-2 text-sm font-semibold text-slate-950">
                      {result.rca.confidence_score}% Confidence
                    </div>
                  </div>

                  <div className="mt-5 grid gap-4 md:grid-cols-2">
                    <div>
                      <h3 className="font-medium text-slate-200">Impact</h3>
                      <p className="mt-2 text-sm text-slate-400">{result.rca.impact}</p>
                    </div>

                    <div>
                      <h3 className="font-medium text-slate-200">Probable Root Cause</h3>
                      <p className="mt-2 text-sm text-slate-400">
                        {result.rca.probable_root_cause}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                  <h2 className="text-lg font-semibold">Extracted Fields</h2>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                    <Field label="Service" value={result.extracted_fields.service || "Unknown"} />
                    <Field label="Severity" value={result.extracted_fields.severity || "Unknown"} />
                    <Field label="Error Type" value={result.extracted_fields.error_type} />
                    <Field label="Metric" value={result.extracted_fields.metric || "Not provided"} />
                  </div>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                  <h2 className="text-lg font-semibold">Evidence</h2>

                  <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-300">
                    {result.rca.evidence.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                  <h2 className="text-lg font-semibold">Suggested Remediation</h2>

                  <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-300">
                    {result.rca.suggested_remediation.map((step) => (
                      <li key={step}>{step}</li>
                    ))}
                  </ol>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                    <h2 className="text-lg font-semibold">Similar Incidents</h2>

                    <div className="mt-4 space-y-3">
                      {result.similar_incidents.map((item) => (
                        <div key={item.incident.id} className="rounded-md bg-slate-950 p-4">
                          <div className="flex justify-between gap-3">
                            <h3 className="font-medium">{item.incident.title}</h3>
                            <span className="text-sm text-cyan-400">Score {item.score}</span>
                          </div>
                          <p className="mt-2 text-sm text-slate-400">
                            {item.incident.root_cause}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="rounded-lg border border-slate-800 bg-slate-900 p-5">
                    <h2 className="text-lg font-semibold">Relevant Runbooks</h2>

                    <div className="mt-4 space-y-3">
                      {result.relevant_runbooks.map((item) => (
                        <div key={item.runbook.id} className="rounded-md bg-slate-950 p-4">
                          <div className="flex justify-between gap-3">
                            <h3 className="font-medium">{item.runbook.alert}</h3>
                            <span className="text-sm text-cyan-400">Score {item.score}</span>
                          </div>
                          <p className="mt-2 text-sm text-slate-400">
                            {item.runbook.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}
          </section>
        </div>
      </div>
    </main>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md bg-slate-950 p-3">
      <p className="text-xs uppercase text-slate-500">{label}</p>
      <p className="mt-1 text-sm text-slate-200">{value}</p>
    </div>
  );
}