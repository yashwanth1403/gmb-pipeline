import { useState, useEffect } from "react";
import { Link, NavLink } from "react-router-dom";
import { CONTACT } from "../config/business";
import Logo from "./Logo";
import Container from "./Container";

const NAV_LINKS = [
  { label: "Cars", to: "/cars" },
  { label: "Sell Car", to: "/sell-car" },
  { label: "About", to: "/about" },
  { label: "Testimonials", to: "/testimonials" },
  { label: "Contact", to: "/contact" },
];


/**
 * Navbar – transparent at top, solid primary on scroll.
 * Mobile: logo left + hamburger right → slide-in drawer from right.
 */
const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [closing, setClosing] = useState(false);

  // Scroll detection
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Lock body scroll when menu is open
  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const openMenu = () => {
    setClosing(false);
    setMenuOpen(true);
  };
  const closeMenu = () => {
    setClosing(true);
    setTimeout(() => {
      setMenuOpen(false);
      setClosing(false);
    }, 200);
  };

  const desktopActiveClass = ({ isActive }: { isActive: boolean }) => {
    if (scrolled) {
      return isActive
        ? "text-logo-blue-light font-semibold border-b-2 border-secondary pb-0.5"
        : "text-primary-foreground opacity-80 hover:opacity-100 transition-opacity";
    }
    return isActive
      ? "text-primary font-semibold border-b-2 border-primary pb-0.5"
      : "text-foreground font-medium opacity-80 hover:opacity-100 transition-opacity";
  };

  const mobileActiveClass = ({ isActive }: { isActive: boolean }) =>
    isActive
      ? "text-logo-blue-light font-semibold"
      : "text-primary-foreground opacity-80 hover:opacity-100 transition-opacity";

  return (
    <>
      {/* ── Navbar bar ──────────────────────────────────────────────── */}
      <header
        className={[
          "fixed inset-x-0 top-0 z-40 transition-all duration-200",
          scrolled ? "bg-primary shadow-md" : "bg-transparent",
        ].join(" ")}
      >
        <Container>
          <nav className="flex h-16 items-center justify-between">
            {/* Logo */}
            <div onClick={closeMenu}>
              <Logo
                className="h-10 sm:h-12"
                textClassName={scrolled ? "text-logo-blue-light" : "text-logo-blue"}
              />
            </div>

            {/* Desktop nav */}
            <div className="hidden items-center gap-6 md:flex">
              {NAV_LINKS.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={desktopActiveClass}
                >
                  {link.label}
                </NavLink>
              ))}

              {/* Call CTA */}
              <a
                href={`tel:+91${CONTACT.phone}`}
                className="ml-2 rounded-full bg-primary px-4 py-1.5 text-sm font-semibold text-white shadow transition-transform hover:scale-105 active:scale-95"
              >
                📞 Call Now
              </a>
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={menuOpen ? closeMenu : openMenu}
              className="flex h-10 w-10 flex-col items-center justify-center gap-[5px] rounded-md md:hidden"
              aria-label={menuOpen ? "Close menu" : "Open menu"}
              aria-expanded={menuOpen}
            >
              <span
                className={[
                  "block h-0.5 w-6 rounded-full transition-all duration-200",
                  scrolled ? "bg-primary-foreground" : "bg-primary",
                  menuOpen ? "translate-y-[7px] rotate-45" : "",
                ].join(" ")}
              />
              <span
                className={[
                  "block h-0.5 w-6 rounded-full transition-all duration-200",
                  scrolled ? "bg-primary-foreground" : "bg-primary",
                  menuOpen ? "opacity-0" : "",
                ].join(" ")}
              />
              <span
                className={[
                  "block h-0.5 w-6 rounded-full transition-all duration-200",
                  scrolled ? "bg-primary-foreground" : "bg-primary",
                  menuOpen ? "-translate-y-[7px] -rotate-45" : "",
                ].join(" ")}
              />
            </button>
          </nav>
        </Container>
      </header>

      {/* ── Mobile overlay ──────────────────────────────────────────── */}
      {menuOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          onClick={closeMenu}
          aria-hidden="true"
        />
      )}

      {/* ── Mobile drawer (slide from right) ────────────────────────── */}
      {menuOpen && (
        <aside
          className={[
            "fixed right-0 top-0 z-50 flex h-full w-72 flex-col bg-primary px-6 py-8 shadow-2xl md:hidden",
            closing ? "menu-slide-out" : "menu-slide-in",
          ].join(" ")}
        >
          {/* Logo + Close */}
          <div className="flex items-center justify-between mb-8">
            <div onClick={closeMenu}>
              <Logo className="h-10" textClassName="text-primary-foreground" />
            </div>
            <button
              onClick={closeMenu}
              className="text-primary-foreground opacity-70 hover:opacity-100 p-1"
              aria-label="Close menu"
            >
              ✕
            </button>
          </div>

          {/* Links */}
          <nav className="flex flex-col gap-5 text-lg font-medium">
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={mobileActiveClass}
                onClick={closeMenu}
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          {/* Call CTA */}
          <a
            href={`tel:+91${CONTACT.phone}`}
            onClick={closeMenu}
            className="mt-10 rounded-full bg-primary py-3 text-center text-sm font-bold text-white shadow-lg"
          >
            📞 Call Now
          </a>
        </aside>
      )}
    </>
  );
};

export default Navbar;
