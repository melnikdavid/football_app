import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../utils/api";

interface Profile {
  full_name: string;
  total_points?: number;
  rank?: string;
}

const RANK_LABELS: Record<string, string> = {
  bronze: "ברונזה 🥉",
  silver: "כסף 🥈",
  gold: "זהב 🥇",
  champion: "אלוף 🏆",
};

export default function Dashboard() {
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    api.get("/profile/me").then((res) => setProfile(res.data)).catch(() => {});
  }, []);

  const firstName = profile?.full_name?.split(" ")[0] || "ספורטאי";

  return (
    <div className="space-y-4">
      {/* Welcome card */}
      <div className="bg-gradient-to-l from-blue-600 to-blue-800 rounded-2xl p-6 text-white">
        <p className="text-blue-200 text-sm">שלום,</p>
        <h2 className="text-2xl font-bold mt-0.5">{firstName} 👋</h2>
        <p className="text-blue-100 text-sm mt-2">מוכן לאימון היום?</p>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-3">
        <Link
          to="/content"
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex flex-col items-center gap-2 hover:shadow-md transition-shadow"
        >
          <span className="text-3xl">🎬</span>
          <span className="text-sm font-medium text-gray-700">תוכן חדש</span>
        </Link>
        <Link
          to="/ai"
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex flex-col items-center gap-2 hover:shadow-md transition-shadow"
        >
          <span className="text-3xl">🤖</span>
          <span className="text-sm font-medium text-gray-700">יועץ אישי</span>
        </Link>
        <Link
          to="/challenges"
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex flex-col items-center gap-2 hover:shadow-md transition-shadow"
        >
          <span className="text-3xl">🏆</span>
          <span className="text-sm font-medium text-gray-700">אתגרים</span>
        </Link>
        <Link
          to="/profile"
          className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex flex-col items-center gap-2 hover:shadow-md transition-shadow"
        >
          <span className="text-3xl">📊</span>
          <span className="text-sm font-medium text-gray-700">הפרופיל שלי</span>
        </Link>
      </div>

      {/* Motivation banner */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
        <p className="text-amber-800 font-medium text-sm">
          💪 "ניצחון מתחיל בתרגול יומיומי"
        </p>
      </div>
    </div>
  );
}
