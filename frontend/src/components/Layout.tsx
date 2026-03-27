import { ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const NAV_ITEMS = [
  { path: "/", label: "דשבורד", icon: "🏠" },
  { path: "/content", label: "תוכן", icon: "🎬" },
  { path: "/challenges", label: "אתגרים", icon: "🏆" },
  { path: "/ai", label: "יועץ AI", icon: "🤖" },
  { path: "/profile", label: "פרופיל", icon: "👤" },
];

export default function Layout({ children }: { children: ReactNode }) {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Top header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="text-lg font-bold text-blue-700">⚽ מועדון הספורטאים</span>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-500 hover:text-red-600 transition-colors"
          >
            יציאה
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-4">
        {children}
      </main>

      {/* Bottom navigation (mobile-first) */}
      <nav className="bg-white border-t border-gray-200 sticky bottom-0 z-40">
        <div className="max-w-2xl mx-auto flex justify-around">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center py-2 px-3 text-xs transition-colors ${
                  isActive
                    ? "text-blue-600 font-semibold"
                    : "text-gray-500 hover:text-blue-500"
                }`}
              >
                <span className="text-xl mb-0.5">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
