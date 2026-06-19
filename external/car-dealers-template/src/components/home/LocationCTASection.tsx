import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { Phone, MapPin, Clock } from "lucide-react";
import { CONTACT, BUSINESS_NAME, BUSINESS_CITY, HOURS } from "@/config/business";

const LocationCTASection = () => {
  return (
    <section className="py-16 sm:py-24 bg-[#0f172a] relative overflow-hidden">
      {/* diagonal accent */}
      <div className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: "linear-gradient(135deg,#fff 25%,transparent 25%),linear-gradient(225deg,#fff 25%,transparent 25%),linear-gradient(45deg,#fff 25%,transparent 25%),linear-gradient(315deg,#fff 25%,transparent 25%)",
          backgroundSize: "20px 20px",
        }}
        aria-hidden
      />
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <Container className="relative">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left: CTA copy */}
          <div className="space-y-6">
            <div className="space-y-3">
              <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">
                Visit us today
              </p>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white leading-tight">
                Come See Us at Our<br />
                <span className="text-logo-blue-light">{BUSINESS_CITY} Showroom</span>
              </h2>
              <p className="text-slate-400 leading-relaxed max-w-md">
                Walk in anytime — no appointment needed. Our team is ready to help you find your perfect car or get the best price for your current one.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-3">
              <Button asChild size="lg" className="gap-2 bg-primary hover:bg-primary-dark text-white font-bold">
                <a href={`tel:+91${CONTACT.phone}`}>
                  <Phone className="h-4 w-4" /> Call Now
                </a>
              </Button>
              <Button asChild size="lg" className="gap-2 bg-transparent border border-white/30 text-white hover:bg-white/10">
                <a href={CONTACT.mapsUrl} target="_blank" rel="noopener noreferrer">
                  <MapPin className="h-4 w-4" /> Get Directions
                </a>
              </Button>
              <Button asChild size="lg" className="gap-2 bg-[#25D366] hover:bg-[#20bd5a] text-white font-bold">
                <a
                  href={`https://wa.me/91${CONTACT.phone}?text=${encodeURIComponent("Hi, I'd like to visit your showroom.")}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2"
                >
                  <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-5 w-5 invert brightness-0" aria-hidden />
                  WhatsApp
                </a>
              </Button>
            </div>
          </div>

          {/* Right: Info cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="rounded-2xl bg-white/5 border border-white/10 p-5 space-y-2">
              <div className="flex items-center gap-2 text-logo-blue-light">
                <MapPin className="h-5 w-5 flex-shrink-0" />
                <span className="text-sm font-semibold uppercase tracking-wider">Address</span>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">{CONTACT.address}</p>
            </div>

            <div className="rounded-2xl bg-white/5 border border-white/10 p-5 space-y-2">
              <div className="flex items-center gap-2 text-logo-blue-light">
                <Phone className="h-5 w-5 flex-shrink-0" />
                <span className="text-sm font-semibold uppercase tracking-wider">Phone</span>
              </div>
              <p className="text-slate-300 text-sm">{CONTACT.phoneFormatted}</p>
              {CONTACT.email && (
                <p className="text-slate-400 text-xs">{CONTACT.email}</p>
              )}
            </div>

            <div className="rounded-2xl bg-white/5 border border-white/10 p-5 space-y-2 sm:col-span-2">
              <div className="flex items-center gap-2 text-logo-blue-light">
                <Clock className="h-5 w-5 flex-shrink-0" />
                <span className="text-sm font-semibold uppercase tracking-wider">Business Hours</span>
              </div>
              <div className="grid grid-cols-2 gap-x-6 gap-y-1">
                {HOURS.map((h) => (
                  <div key={h.days} className="flex justify-between text-sm">
                    <span className="text-slate-400">{h.days}</span>
                    <span className="text-slate-200 font-medium">{h.hours}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
};

export default LocationCTASection;
