import { useEffect, useState } from "react";
import api from "../utils/api";

interface Challenge {
  id: string;
  title: string;
  description: string | null;
  points: number;
  type: string;
  start_date: string | null;
  end_date: string | null;
}

interface UserPoints {
  total_points: number;
  rank: string;
}

const RANK_DISPLAY: Record<string, { label: string; color: string }> = {
  bronze: { label: "ברונזה", color: "text-amber-700" },
  silver: { label: "כסף", color: "text-gray-500" },
  gold: { label: "זהב", color: "text-yellow-500" },
  champion: { label: "אלוף", color: "text-blue-600" },
};

export default function Challenges() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [points, setPoints] = useState<UserPoints | null>(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.get("/challenges?status=active"),
      api.get("/profile/me").then(() => {}).catch(() => {}),
    ])
      .then(([chalRes]) => setChallenges(chalRes.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleComplete = async (challengeId: string) => {
    setCompleting(challengeId);
    try {
      const { data } = await api.post(`/challenges/${challengeId}/complete`, {});
      setPoints(data);
      setChallenges((prev) => prev.filter((c) => c.id !== challengeId));
    } catch {
      alert("לא ניתן להשלים את האתגר — ייתכן שכבר השלמת אותו");
    } finally {
      setCompleting(null);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-gray-900">אתגרים</h1>

      {/* Points card */}
      {points && (
        <div className="bg-gradient-to-l from-yellow-400 to-amber-500 rounded-xl p-4 text-white">
          <p className="text-sm font-medium opacity-90">הניקוד שלך</p>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-3xl font-bold">{points.total_points}</span>
            <span className="text-sm">נקודות</span>
          </div>
          <p className={`text-sm mt-1 font-semibold ${RANK_DISPLAY[points.rank]?.color || ""}`}>
            דרגה: {RANK_DISPLAY[points.rank]?.label || points.rank}
          </p>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-gray-400">טוען אתגרים...</div>
      ) : challenges.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-5xl mb-3">🏆</div>
          <p className="text-gray-500">אין אתגרים פעילים כרגע</p>
          <p className="text-gray-400 text-sm mt-1">בדוק שוב מחר!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {challenges.map((challenge) => (
            <div
              key={challenge.id}
              className="bg-white rounded-xl shadow-sm border border-gray-100 p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{challenge.title}</h3>
                  {challenge.description && (
                    <p className="text-sm text-gray-500 mt-1">{challenge.description}</p>
                  )}
                  <span className="inline-block mt-2 text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                    +{challenge.points} נקודות
                  </span>
                </div>
                <button
                  onClick={() => handleComplete(challenge.id)}
                  disabled={completing === challenge.id}
                  className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50 flex-shrink-0"
                >
                  {completing === challenge.id ? "..." : "השלמתי"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
