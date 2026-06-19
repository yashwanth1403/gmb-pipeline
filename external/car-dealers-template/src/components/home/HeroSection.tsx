import { Link } from "react-router-dom";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { HERO } from "@/config/business";

const HeroSection = () => {
  return (
    <section className="relative bg-primary py-20 sm:py-32 overflow-hidden">
      {/* Background image */}
      {HERO.backgroundDesktop && (
        <img
          src={HERO.backgroundDesktop}
          alt=""
          aria-hidden
          className="absolute inset-0 w-full h-full object-cover object-center"
        />
      )}
      {/* Dark gradient overlay — stronger at edges, lighter in centre for photo detail */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/75 via-black/55 to-black/75" aria-hidden />

      <Container className="relative z-10 flex flex-col items-center text-center space-y-6">
        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-5xl max-w-2xl drop-shadow-[0_2px_16px_rgba(0,0,0,0.8)]">
          {HERO.headline}
        </h1>
        <p className="text-lg text-white/85 max-w-md drop-shadow-[0_1px_8px_rgba(0,0,0,0.8)]">
          {HERO.subheadline}
        </p>
        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto pt-2">
          <Button
            asChild
            size="lg"
            className="w-full sm:w-auto text-base px-8 bg-white text-primary font-bold hover:bg-white/95 shadow-lg"
          >
            <Link to="/cars">View Cars</Link>
          </Button>
          <Button
            asChild
            size="lg"
            className="w-full sm:w-auto text-base px-8 bg-white/10 backdrop-blur-sm border-2 border-white text-white font-bold hover:bg-white/20"
          >
            <Link to="/sell-car">Sell Your Car</Link>
          </Button>
        </div>
      </Container>
    </section>
  );
};

export default HeroSection;
