import { BUSINESS_NAME, BUSINESS_CITY, CONTACT } from "@/config/business";
import { Phone, MessageCircle, MapPin } from "lucide-react";

export const ContactHeader = () => (
  <section className="bg-[#0f172a] py-14 sm:py-20 relative overflow-hidden">
    {/* grid bg */}
    <div
      className="absolute inset-0 opacity-[0.04]"
      style={{ backgroundImage: "linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)", backgroundSize: "40px 40px" }}
      aria-hidden
    />
    <div className="relative max-w-3xl mx-auto text-center space-y-5">
      <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">Get in touch</p>
      <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
        Contact {BUSINESS_NAME}
      </h1>
      <p className="text-slate-400 text-base sm:text-lg max-w-xl mx-auto">
        We're here to help you find the right car in {BUSINESS_CITY}. Reach us by phone, WhatsApp, or visit our showroom.
      </p>

      {/* Quick contact pills */}
      <div className="flex flex-wrap justify-center gap-3 pt-2">
        <a
          href={`tel:+91${CONTACT.phone}`}
          className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 border border-white/15 text-white rounded-full px-5 py-2 text-sm font-medium transition-colors"
        >
          <Phone className="h-4 w-4 text-logo-blue-light" />
          {CONTACT.phoneFormatted}
        </a>
        <a
          href={`https://wa.me/91${CONTACT.phone}`}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 bg-[#25D366]/20 hover:bg-[#25D366]/30 border border-[#25D366]/30 text-white rounded-full px-5 py-2 text-sm font-medium transition-colors"
        >
          <MessageCircle className="h-4 w-4 text-[#25D366]" />
          WhatsApp us
        </a>
        <a
          href={CONTACT.mapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 border border-white/15 text-white rounded-full px-5 py-2 text-sm font-medium transition-colors"
        >
          <MapPin className="h-4 w-4 text-logo-blue-light" />
          Get Directions
        </a>
      </div>
    </div>
  </section>
);
