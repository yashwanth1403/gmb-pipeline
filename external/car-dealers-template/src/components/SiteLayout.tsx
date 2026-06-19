import { ReactNode } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import WhatsAppButton from "@/components/WhatsAppButton";

/**
 * SiteLayout – wraps every public page.
 * - Sticky Navbar (transparent → solid on scroll)
 * - Footer
 * - Floating WhatsApp button
 * - pt-16 to offset fixed navbar height
 */
const SiteLayout = ({ children }: { children: ReactNode }) => {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1 pt-16">{children}</main>
      <Footer />
      <WhatsAppButton />
    </div>
  );
};

export default SiteLayout;
