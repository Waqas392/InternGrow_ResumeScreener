import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTheme } from "../hooks/useTheme";
import { Button } from "./Button";

export function NavBar() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const linkClassName = ({ isActive }: { isActive: boolean }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
      isActive
        ? "bg-slate-200 text-slate-900 dark:bg-slate-800 dark:text-white"
        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white"
    }`;

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3">
        <div className="flex items-center gap-6">
          <NavLink
            to="/"
            className="text-lg font-semibold tracking-tight focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
          >
            InternGrow Resume Screening
          </NavLink>
          {user && (
            <nav className="flex items-center gap-2" aria-label="Primary">
              <NavLink to="/" className={linkClassName} end>
                Dashboard
              </NavLink>
              <NavLink to="/resumes" className={linkClassName}>
                Resumes
              </NavLink>
              <NavLink to="/evaluation" className={linkClassName}>
                Evaluation
              </NavLink>
            </nav>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={toggleTheme} aria-label="Toggle dark mode">
            {theme === "dark" ? "Light" : "Dark"}
          </Button>
          {user && (
            <Button
              variant="ghost"
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              Logout
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
