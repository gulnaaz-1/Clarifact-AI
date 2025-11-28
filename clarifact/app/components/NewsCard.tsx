"use client";

import { useState } from "react";
import Link from "next/link";

export default function NewsCard({ item }: any) {
  const risk = item.risk?.risk_score ?? 0;

  const color =
    risk > 0.75 ? "bg-red-500" :
    risk > 0.50 ? "bg-orange-500" :
    risk > 0.25 ? "bg-yellow-500" :
    "bg-green-500";

  return (
    <div className="p-4 border rounded-lg shadow-md mb-4 flex gap-4">
      {item.image && (
        <img src={item.image} className="w-32 h-24 object-cover rounded" />
      )}

      <div className="flex flex-col w-full">
        <h2 className="font-semibold text-lg">{item.title}</h2>
        <p className="text-sm text-gray-500">{item.text?.slice(0,120)}...</p>

        <div className="flex items-center mt-2 gap-2">
          <div className={`w-4 h-4 rounded-full ${color}`} />
          <span className="text-sm font-medium">Risk: {(risk*100).toFixed(1)}%</span>
        </div>

        <Link
          href={`/analyze?title=${encodeURIComponent(item.title)}&url=${encodeURIComponent(item.url)}&text=${encodeURIComponent(item.text)}`}
          className="text-blue-500 text-sm mt-2 underline"
        >
          View analysis →
        </Link>
      </div>
    </div>
  );
}
