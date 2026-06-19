import { Link } from "react-router-dom";
import { BUSINESS_NAME, BUSINESS_CITY, RATING } from "@/config/business";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { Star, ShieldCheck, BadgeIndianRupee } from "lucide-react";

const AboutHero = () => (
  <section className="bg-[#0f172a] py-16 sm:py-24 relative overflow-hidden">
    {/* grid bg */}
    <div
      className="absolute inset-0 opacity-[0.04]"
      style={{ backgroundImage: "linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)", backgroundSize: "40px 40px" }}
      aria-hidden
    />
    {/* glow */}
    <div className="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-primary/10 blur-3xl pointer-events-none -translate-y-1/2 translate-x-1/4" />

    <Container className="relative">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left */}
        <div className="space-y-6">
          <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">
            About {BUSINESS_NAME}
          </p>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Trusted Pre-Owned Car Dealer in{" "}
            <span className="text-logo-blue-light">{BUSINESS_CITY}</span>
          </h1>
          <p className="text-slate-400 text-base leading-relaxed max-w-lg">
            {BUSINESS_NAME} helps {BUSINESS_CITY} customers buy and sell pre-owned cars with honest pricing, verified vehicles, and easy finance options.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <Button asChild size="lg" className="bg-primary hover:bg-primary-dark text-white font-bold px-8">
              <Link to="/cars">View Cars</Link>
            </Button>
            <Button asChild size="lg" className="bg-transparent border border-white/30 text-white hover:bg-white/10 px-8">
              <Link to="/sell-car">Sell Your Car</Link>
            </Button>
          </div>
        </div>

        {/* Right: trust badges */}
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-2xl bg-white/5 border border-white/10 p-5 flex flex-col gap-3">
            <div className="flex gap-0.5">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} className="h-4 w-4 fill-logo-blue text-logo-blue-light" />
              ))}
            </div>
            <p className="text-3xl font-black text-white">{RATING.score}<span className="text-slate-400 text-lg font-semibold">/{RATING.outOf}</span></p>
            <p className="text-slate-400 text-sm">Google Rating</p>
          </div>

          <div className="rounded-2xl bg-white/5 border border-white/10 p-5 flex flex-col gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400 to-blue-500 flex items-center justify-center">
              <ShieldCheck className="h-5 w-5 text-white" />
            </div>
            <p className="text-3xl font-black text-white">{RATING.totalCustomers}</p>
            <p className="text-slate-400 text-sm">Happy Customers</p>
          </div>

          <div className="col-span-2 rounded-2xl bg-gradient-to-br from-primary/10 to-primary/20 border border-primary/30 p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-logo-blue to-primary flex items-center justify-center flex-shrink-0">
              <BadgeIndianRupee className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-white font-bold">Transparent Pricing</p>
              <p className="text-slate-400 text-sm">No hidden charges, ever</p>
            </div>
          </div>
        </div>
      </div>
    </Container>
  </section>
);

export default AboutHero;
