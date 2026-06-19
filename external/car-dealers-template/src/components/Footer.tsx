import { Link } from "react-router-dom";
import { Instagram } from "lucide-react";
import { BUSINESS_NAME, CONTACT } from "../config/business";
import Logo from "./Logo";
import Container from "./Container";

const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-primary text-primary-foreground">
      <Container className="py-10">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {/* Brand */}
          <div>
            <Logo className="h-10" textClassName="text-primary-foreground" />
            <p className="mt-2 text-sm opacity-75">
              {CONTACT.address}
              <br />
              Quality pre-owned cars you can trust.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-white">
              Quick Links
            </h3>
            <ul className="space-y-2 text-sm">
              {[
                { label: "Browse Cars", to: "/cars" },
                { label: "Sell Your Car", to: "/sell-car" },
                { label: "About Us", to: "/about" },
                { label: "Testimonials", to: "/testimonials" },
                { label: "Contact", to: "/contact" },
              ].map((link) => (
                <li key={link.to}>
                  <Link
                    to={link.to}
                    className="opacity-75 transition-opacity hover:opacity-100"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-white">
              Contact
            </h3>
            <ul className="space-y-2 text-sm opacity-75">
              <li><a href={`tel:+91${CONTACT.phone}`} className="hover:underline">📞 {CONTACT.phoneFormatted}</a></li>
              <li><a href={`mailto:${CONTACT.email}`} className="hover:underline">📧 {CONTACT.email}</a></li>
              <li><a href={CONTACT.mapsUrl} target="_blank" rel="noopener noreferrer" className="hover:underline">📍 {CONTACT.address}</a></li>
              <li><a href={CONTACT.instagram} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 hover:underline"><Instagram size={16} className="shrink-0" /> Instagram</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-primary-foreground/20 pt-6 text-center text-xs opacity-50">
          © {year} {BUSINESS_NAME}. All rights reserved.
        </div>
      </Container>
    </footer>
  );
};

export default Footer;
