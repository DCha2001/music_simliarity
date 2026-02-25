'use client'

import { useState } from "react";

export default function Home() {
  const [title, setTitle] = useState("");
  const [artist, setArtist] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({title: title, artist: artist }),
      });


      if (!res.ok) throw new Error("Failed to fetch results");

      const data = await res.json();

      console.log(data);  

      setResult(data);
    } catch (err) {
      console.error(err);
      setResult({ error: "Something went wrong." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-gray-800 p-6">
      <div className="bg-gray-950/60 backdrop-blur-xl border border-gray-800 rounded-2xl shadow-lg w-full max-w-md p-8">
        <h1 className="text-2xl font-semibold text-white mb-6 text-center">
          Music Similarity Finder
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="string"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-gray-900 text-gray-100 placeholder-gray-500 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
          />
          <input
            type="string"
            placeholder="Artist"
            value={artist}
            onChange={(e) => setArtist(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-gray-900 text-gray-100 placeholder-gray-500 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition duration-200 shadow-md hover:shadow-lg disabled:opacity-50"
          >
            {loading ? "Searching..." : "Find Similar Music"}
          </button>
        </form>

        {result && (
          <div className="mt-6 p-4 rounded-lg bg-gray-900 border border-gray-800 text-gray-200">
            {result.status === "error" ? (
              <p className="text-red-400">{result.message}</p>
            ) : (
                  <div className="p-6">
                    <h1 className="text-2xl font-bold mb-4">Songs</h1>
                    <ul className="space-y-2">
                      {result.songs.map((song :any) => (
                        <li
                          key={song.id}
                          className="p-4  rounded-xl bg-gray-800 shadow-sm hover:bg-gray-700 transition"
                        >
                          <p className="text-lg font-semibold">{song.title}</p>
                          <p className="text-sm text-gray-600">{song.artist}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}