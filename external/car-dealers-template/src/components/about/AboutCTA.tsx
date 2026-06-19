import { Link } from "react-router-dom";
import { BUSINESS_NAME, CONTACT } from "@/config/business";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";

const AboutCTA = () => (
  <section className="py-14 sm:py-20 bg-primary">
    <Container>
      <div className="flex flex-col items-center text-center gap-6 max-w-xl mx-auto">
        <h2 className="text-2xl sm:text-4xl font-extrabold text-primary-foreground">
          Looking for your next car?
        </h2>
        <p className="text-primary-foreground/75 text-base">
          Browse our verified inventory or get in touch with our team today.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <Button asChild size="lg" className="bg-primary text-white hover:bg-primary/90 font-bold px-8">
            <Link to="/cars">Browse Cars</Link>
          </Button>
          <Button asChild size="lg" className="bg-transparent border border-white/30 text-white hover:bg-white/10 px-8">
            <Link to="/contact">Contact Us</Link>
          </Button>
          <Button asChild size="lg" className="bg-[#25D366] text-white hover:bg-[#20bd5a] font-bold px-8 gap-2">
            <a href={`https://wa.me/91${CONTACT.phone}?text=${encodeURIComponent(`Hello! I'm interested in buying a car from ${BUSINESS_NAME}.`)}`} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center gap-2">
              <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-5 w-5 invert brightness-0" aria-hidden />
              WhatsApp
            </a>
          </Button>
        </div>
      </div>
    </Container>
  </section>
);

export default AboutCTA;
