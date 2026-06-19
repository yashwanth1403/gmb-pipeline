import React from "react";
import { PhoneCall } from "lucide-react";
import { CONTACT, BUSINESS_CITY } from "@/config/business";

export const ContactCTA = () => {
  return (
    <div className="bg-gradient-to-br from-primary via-primary-dark to-primary rounded-xl mt-16 p-8 text-center shadow-lg relative overflow-hidden group">
      {/* Decorative Blur Backgrounds */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-32 h-32 rounded-full bg-white opacity-10 blur-2xl group-hover:scale-150 transition-transform duration-700"></div>
      <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-48 h-48 rounded-full bg-white opacity-5 blur-3xl group-hover:scale-125 transition-transform duration-700 delay-100"></div>

      <div className="relative z-10 max-w-2xl mx-auto flex flex-col items-center">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-white mb-3">
          Looking for the best pre-owned car deals in {BUSINESS_CITY}?
        </h2>
        <p className="text-primary-foreground/80 mb-8 font-medium">
          Get in touch with us instantly or schedule a showroom visit to test
          drive your next car.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center max-w-md mx-auto">
          <a
            href={`tel:+91${CONTACT.phone}`}
            className="flex-1 bg-white hover:bg-white/90 text-primary flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl font-extrabold transition-all shadow-md hover:shadow-lg hover:-translate-y-1"
          >
            <PhoneCall size={20} />
            Call Now
          </a>
          <a
            href={`https://wa.me/91${CONTACT.phone}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-[#25D366] hover:bg-[#20bd5a] text-white flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl font-extrabold transition-all shadow-md hover:shadow-lg hover:-translate-y-1"
          >
            <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-5 w-5 invert brightness-0" aria-hidden />
            WhatsApp Now
          </a>
        </div>
      </div>
    </div>
  );
};
