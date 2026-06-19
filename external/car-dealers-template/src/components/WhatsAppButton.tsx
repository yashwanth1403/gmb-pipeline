/**
 * WhatsAppButton – Fixed bottom-right floating button.
 * Pulse animation every 6s via CSS keyframe in index.css.
 */

import { BUSINESS_NAME, CONTACT } from "@/config/business";

const WHATSAPP_MESSAGE = encodeURIComponent(
  `Hello! I'm interested in a car from ${BUSINESS_NAME}.`
);

const WhatsAppButton = () => {
  const href = `https://wa.me/91${CONTACT.phone}?text=${WHATSAPP_MESSAGE}`;

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Chat with us on WhatsApp"
      className="whatsapp-pulse fixed bottom-6 right-4 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] text-white shadow-lg transition-transform duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-[#25D366] focus:ring-offset-2"
    >
      <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-7 w-7 invert brightness-0" aria-hidden />
    </a>
  );
};

export default WhatsAppButton;
