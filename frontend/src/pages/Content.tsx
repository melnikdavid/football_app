import { useEffect, useState } from "react";
import api from "../utils/api";

interface ContentItem {
  id: string;
  type: string;
  title: string;
  description: string | null;
  vimeo_id: string | null;
  thumbnail_url: string | null;
  duration_sec: number | null;
  topic_category: string | null;
}

const TYPE_LABELS: Record<string, string> = {
  video: "וידאו 🎬",
  zoom: "זום 📹",
  podcast: "פודקאסט 🎙️",
  challenge: "אתגר 🏆",
  article: "מאמר 📝",
};

const CATEGORIES = ["הכל", "כדורגל", "תזונה", "כושר", "מנטלי", "טקטיקה"];

export default function Content() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("הכל");
  const [selected, setSelected] = useState<ContentItem | null>(null);

  useEffect(() => {
    setLoading(true);
    const params: Record<string, string> = {};
    if (category !== "הכל") params.category = category;
    api.get("/content", { params })
      .then((res) => setItems(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [category]);

  const handleView = async (item: ContentItem) => {
    setSelected(item);
    await api.post(`/content/${item.id}/view`, { completion_pct: 0 }).catch(() => {});
  };

  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-gray-900">תוכן</h1>

      {/* Category filter */}
      <div className="flex gap-2 overflow-x-auto pb-1 no-scrollbar" dir="rtl">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`whitespace-nowrap px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              category === cat
                ? "bg-blue-600 text-white"
                : "bg-white border border-gray-200 text-gray-600 hover:border-blue-300"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Vimeo player modal */}
      {selected && selected.vimeo_id && (
        <div
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="bg-black rounded-xl overflow-hidden w-full max-w-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="aspect-video">
              <iframe
                src={`https://player.vimeo.com/video/${selected.vimeo_id}?autoplay=1&dnt=1`}
                className="w-full h-full"
                allow="autoplay; fullscreen; picture-in-picture"
                allowFullScreen
                title={selected.title}
              />
            </div>
            <div className="p-4">
              <h3 className="text-white font-semibold">{selected.title}</h3>
              <button
                onClick={() => setSelected(null)}
                className="mt-3 text-gray-400 text-sm hover:text-white"
              >
                סגור
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Content list */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">טוען תוכן...</div>
      ) : items.length === 0 ? (
        <div className="text-center py-12 text-gray-400">אין תוכן זמין כרגע</div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              onClick={() => handleView(item)}
              className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex cursor-pointer hover:shadow-md transition-shadow active:scale-[0.99]"
            >
              {item.thumbnail_url ? (
                <img
                  src={item.thumbnail_url}
                  alt={item.title}
                  className="w-28 h-20 object-cover flex-shrink-0"
                />
              ) : (
                <div className="w-28 h-20 bg-blue-100 flex items-center justify-center flex-shrink-0 text-3xl">
                  🎬
                </div>
              )}
              <div className="p-3 flex-1 min-w-0">
                <span className="text-xs text-blue-600 font-medium">
                  {TYPE_LABELS[item.type] || item.type}
                </span>
                <h3 className="text-sm font-semibold text-gray-900 mt-0.5 line-clamp-2">
                  {item.title}
                </h3>
                {item.duration_sec && (
                  <p className="text-xs text-gray-400 mt-1">{formatDuration(item.duration_sec)}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
