import { Link } from "react-router-dom";
import Container from "@/components/Container";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { RATING } from "@/config/business";

const RatingHighlight = () => (
  <section className="py-16 sm:py-24 bg-[#0f172a] relative overflow-hidden">
    <div
      className="absolute inset-0 opacity-[0.04]"
      style={{ backgroundImage: "linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)", backgroundSize: "40px 40px" }}
      aria-hidden
    />
    <Container className="relative">
      <div className="max-w-3xl mx-auto rounded-3xl bg-white/5 border border-white/10 p-8 sm:p-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-10 items-center">
          {/* Score */}
          <div className="text-center sm:text-left space-y-4">
            <div className="flex justify-center sm:justify-start gap-1">
              {Array.from({ length: RATING.outOf }).map((_, i) => (
                <Star key={i} className="h-7 w-7 fill-logo-blue text-logo-blue-light" />
              ))}
            </div>
            <div>
              <p className="text-7xl font-black text-white leading-none">{RATING.score}</p>
              <p className="text-slate-400 text-sm mt-1">out of {RATING.outOf} · Google Reviews</p>
            </div>
            <div className="inline-flex items-center gap-2 bg-blue-500/20 border border-blue-500/30 rounded-full px-4 py-1.5">
              <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
              <span className="text-blue-300 text-sm font-semibold">{RATING.totalCustomers} Happy Customers</span>
            </div>
          </div>

          {/* Tagline + CTA */}
          <div className="space-y-5 text-center sm:text-left">
            <div className="space-y-2">
              <p className="text-xl font-bold text-white leading-snug">{RATING.tagline}</p>
              <p className="text-slate-400 text-sm leading-relaxed">
                Consistent 5-star experiences built on honest pricing, verified cars, and helpful service.
              </p>
            </div>
            <Button asChild size="lg" className="bg-primary hover:bg-primary-dark text-white font-bold w-full sm:w-auto">
              <Link to="/contact">Contact Dealer →</Link>
            </Button>
          </div>
        </div>
      </div>
    </Container>
  </section>
);

export default RatingHighlight;
