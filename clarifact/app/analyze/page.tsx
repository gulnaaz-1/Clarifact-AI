"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { analyzePost } from "../lib/api";

export default function AnalyzePage() {
  const params = useSearchParams();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const title = params.get("title") || "";
    const text = params.get("text") || "";
    const url = params.get("url") || "";

    analyzePost({ title, text, url }).then(setData);
  }, []);

  if (!data) return <div className="p-8">Loading…</div>;

  const risk = data.risk.risk_score;

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-2xl font-bold">{data.title}</h1>

      <p className="text-gray-700">{data.text}</p>

      <h3 className="font-semibold text-xl">Risk Score: {(risk*100).toFixed(1)}%</h3>

      <pre className="p-4 bg-gray-900 text-white rounded-lg">
        {JSON.stringify(data.risk, null, 2)}
      </pre>

      <h3 className="font-semibold text-lg">Detected Location:</h3>
      <p>{data.geolocation}</p>

      <h3 className="font-semibold text-lg">Claims Found:</h3>
      <ul className="list-disc ml-6">
        {data.risk.claims.map((c: string, i: number) =>
          <li key={i}>{c}</li>
        )}
      </ul>
    </div>
  );
}
