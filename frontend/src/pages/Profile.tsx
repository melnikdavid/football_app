import { useEffect, useState, FormEvent } from "react";
import api from "../utils/api";

interface Profile {
  full_name: string;
  age: number | null;
  position: string | null;
  team: string | null;
  city: string | null;
  weight: number | null;
  height: number | null;
  training_frequency: number | null;
  phone: string | null;
}

const POSITIONS = ["שוער", "בלם", "מגן", "קשר", "כנף", "חלוץ"];

export default function Profile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.get("/profile/me")
      .then((res) => setProfile(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    try {
      await api.put("/profile/me", profile);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      alert("שגיאה בשמירה");
    } finally {
      setSaving(false);
    }
  };

  const update = (field: keyof Profile, value: string | number | null) => {
    setProfile((prev) => prev ? { ...prev, [field]: value } : prev);
  };

  if (loading) return <div className="text-center py-12 text-gray-400">טוען פרופיל...</div>;
  if (!profile) return <div className="text-center py-12 text-gray-400">שגיאה בטעינת הפרופיל</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-gray-900">הפרופיל שלי</h1>

      <form onSubmit={handleSave} className="space-y-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-4">
          <h2 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">מידע אישי</h2>

          <Field label="שם מלא">
            <input
              type="text"
              value={profile.full_name}
              onChange={(e) => update("full_name", e.target.value)}
              className={inputCls}
            />
          </Field>

          <Field label="גיל">
            <input
              type="number"
              value={profile.age ?? ""}
              onChange={(e) => update("age", e.target.value ? Number(e.target.value) : null)}
              className={inputCls}
              min={8}
              max={50}
            />
          </Field>

          <Field label="טלפון">
            <input
              type="tel"
              value={profile.phone ?? ""}
              onChange={(e) => update("phone", e.target.value || null)}
              className={inputCls}
              dir="ltr"
            />
          </Field>

          <Field label="עיר">
            <input
              type="text"
              value={profile.city ?? ""}
              onChange={(e) => update("city", e.target.value || null)}
              className={inputCls}
            />
          </Field>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-4">
          <h2 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">פרטי כדורגל</h2>

          <Field label="עמדה">
            <select
              value={profile.position ?? ""}
              onChange={(e) => update("position", e.target.value || null)}
              className={inputCls}
            >
              <option value="">בחר עמדה</option>
              {POSITIONS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </Field>

          <Field label="קבוצה">
            <input
              type="text"
              value={profile.team ?? ""}
              onChange={(e) => update("team", e.target.value || null)}
              className={inputCls}
            />
          </Field>

          <Field label="אימונים בשבוע">
            <input
              type="number"
              value={profile.training_frequency ?? ""}
              onChange={(e) => update("training_frequency", e.target.value ? Number(e.target.value) : null)}
              className={inputCls}
              min={1}
              max={7}
            />
          </Field>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-4">
          <h2 className="font-semibold text-gray-700 text-sm uppercase tracking-wide">נתוני גוף</h2>

          <Field label="גובה (ס״מ)">
            <input
              type="number"
              value={profile.height ?? ""}
              onChange={(e) => update("height", e.target.value ? Number(e.target.value) : null)}
              className={inputCls}
            />
          </Field>

          <Field label="משקל (ק״ג)">
            <input
              type="number"
              value={profile.weight ?? ""}
              onChange={(e) => update("weight", e.target.value ? Number(e.target.value) : null)}
              className={inputCls}
            />
          </Field>
        </div>

        <button
          type="submit"
          disabled={saving}
          className={`w-full py-3 rounded-xl font-semibold text-white transition-colors ${
            saved ? "bg-green-600" : "bg-blue-600 hover:bg-blue-700"
          } disabled:opacity-50`}
        >
          {saved ? "נשמר ✓" : saving ? "שומר..." : "שמור שינויים"}
        </button>
      </form>
    </div>
  );
}

const inputCls = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm text-gray-600 mb-1">{label}</label>
      {children}
    </div>
  );
}
