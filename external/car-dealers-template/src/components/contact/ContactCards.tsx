import { PhoneCall, MapPin, MessageCircle } from "lucide-react";
import { CONTACT } from "@/config/business";

export const ContactCards = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-12">
    <a
      href={`tel:+91${CONTACT.phone}`}
      className="group rounded-2xl bg-gradient-to-br from-primary/10 to-primary/20 border border-primary/20 p-6 flex flex-col items-center text-center gap-3 hover:-translate-y-1 hover:shadow-lg transition-all duration-300"
    >
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-logo-blue to-primary flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
        <PhoneCall className="h-7 w-7 text-white" />
      </div>
      <div>
        <h3 className="font-bold text-foreground text-base">Call Us</h3>
        <p className="text-muted-foreground text-sm mt-0.5">{CONTACT.phoneFormatted}</p>
      </div>
    </a>

    <a
      href={`https://wa.me/91${CONTACT.phone}`}
      target="_blank"
      rel="noopener noreferrer"
      className="group rounded-2xl bg-[#25D366]/10 border border-[#25D366]/20 p-6 flex flex-col items-center text-center gap-3 hover:-translate-y-1 hover:shadow-lg transition-all duration-300"
    >
      <div className="w-14 h-14 rounded-2xl bg-[#25D366] flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
        <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-7 w-7 invert brightness-0" aria-hidden />
      </div>
      <div>
        <h3 className="font-bold text-foreground text-base">WhatsApp</h3>
        <p className="text-muted-foreground text-sm mt-0.5">Chat instantly</p>
      </div>
    </a>

    <a
      href={CONTACT.mapsUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="group rounded-2xl bg-gradient-to-br from-blue-500/10 to-violet-500/10 border border-blue-500/20 p-6 flex flex-col items-center text-center gap-3 hover:-translate-y-1 hover:shadow-lg transition-all duration-300"
    >
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
        <MapPin className="h-7 w-7 text-white" />
      </div>
      <div>
        <h3 className="font-bold text-foreground text-base">Visit Showroom</h3>
        <p className="text-muted-foreground text-sm mt-0.5 line-clamp-2">{CONTACT.address}</p>
      </div>
    </a>
  </div>
);
