import { Link } from "react-router-dom";
import { BUSINESS_NAME, CONTACT, RATING } from "@/config/business";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";

const WHATSAPP_MSG = encodeURIComponent("Hello! I saw your customer reviews and I'm interested in buying a car.");

const TestimonialsCTA = () => (
  <section className="py-14 sm:py-20 bg-primary">
    <Container>
      <div className="flex flex-col items-center text-center gap-6 max-w-xl mx-auto">
        <h2 className="text-2xl sm:text-4xl font-extrabold text-primary-foreground">
          Ready to buy your next car?
        </h2>
        <p className="text-primary-foreground/75 text-base">
          Join {RATING.totalCustomers} happy customers who found their car through {BUSINESS_NAME}.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <Button asChild size="lg" className="bg-primary text-white hover:bg-primary/90 font-bold px-8">
            <Link to="/cars">View Available Cars</Link>
          </Button>
          <Button asChild size="lg" className="bg-[#25D366] text-white hover:bg-[#20bd5a] font-bold px-8 gap-2">
            <a href={`https://wa.me/91${CONTACT.phone}?text=${WHATSAPP_MSG}`} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center gap-2">
              <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-5 w-5 invert brightness-0" aria-hidden />
              WhatsApp Dealer
            </a>
          </Button>
        </div>
      </div>
    </Container>
  </section>
);

export default TestimonialsCTA;
