import Container from "@/components/Container";
import { Link } from "react-router-dom";
import { Car, BadgeIndianRupee, ArrowLeftRight } from "lucide-react";
import { CONTACT, BUSINESS_NAME } from "@/config/business";

const SERVICES = [
  {
    icon: Car,
    title: "Buy a Car",
    desc: "Browse our verified, non-accident pre-owned cars. Every car comes with service history and odometer check.",
    cta: "Browse Cars",
    href: "/cars",
    isInternal: true,
    style: "bg-primary text-white",
    btnStyle: "bg-white text-primary hover:bg-white/90",
    waText: `Hi! I'm looking to buy a car from ${BUSINESS_NAME}.`,
  },
  {
    icon: BadgeIndianRupee,
    title: "Sell Your Car",
    desc: "Get the best price for your car. Quick inspection, instant quote, same-day payment. No middlemen.",
    cta: "Get a Quote",
    href: "/sell-car",
    isInternal: true,
    style: "bg-[#0f172a] text-white",
    btnStyle: "bg-primary text-white hover:bg-primary/90",
    waText: `Hi! I want to sell my car. Can you help me with a quote?`,
  },
  {
    icon: ArrowLeftRight,
    title: "Exchange Your Car",
    desc: "Upgrade your current car hassle-free. Trade it in and drive out the same day with your new set of wheels.",
    cta: "Exchange Now",
    href: null,
    isInternal: false,
    style: "bg-white border border-border text-foreground",
    btnStyle: "bg-primary text-white hover:bg-primary/90",
    waText: `Hi! I'd like to exchange my current car for another one at ${BUSINESS_NAME}.`,
  },
];

const BuySellExchangeSection = () => (
  <section className="py-16 sm:py-24 bg-slate-50">
    <Container className="space-y-10">
      <div className="text-center space-y-2">
        <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">
          Our Services
        </p>
        <h2 className="text-3xl font-extrabold sm:text-4xl text-foreground">
          Buy &bull; Sell &bull; Exchange
        </h2>
        <p className="text-muted-foreground max-w-md mx-auto">
          One stop for all your car needs — reach us instantly on WhatsApp
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {SERVICES.map(({ icon: Icon, title, desc, cta, href, isInternal, style, btnStyle, waText }) => (
          <div key={title} className={`rounded-2xl p-7 flex flex-col gap-5 shadow-sm ${style}`}>
            <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
              <Icon className="h-6 w-6" />
            </div>
            <div className="flex-1 space-y-2">
              <h3 className="text-xl font-bold">{title}</h3>
              <p className="text-sm leading-relaxed opacity-80">{desc}</p>
            </div>
            <div className="flex flex-col gap-2">
              {isInternal && href ? (
                <Link
                  to={href}
                  className={`inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-bold transition-all ${btnStyle}`}
                >
                  {cta}
                </Link>
              ) : null}
              <a
                href={`https://wa.me/91${CONTACT.phone}?text=${encodeURIComponent(waText)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#25D366] px-5 py-2.5 text-sm font-bold text-white hover:bg-[#20bd5a] transition-all"
              >
                <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-4 w-4 invert brightness-0" aria-hidden />
                WhatsApp Us
              </a>
            </div>
          </div>
        ))}
      </div>
    </Container>
  </section>
);

export default BuySellExchangeSection;
