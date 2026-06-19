import { Phone } from "lucide-react";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { CONTACT } from "@/config/business";

const SellCarCTA = () => {
  const scrollToForm = () => {
    document.getElementById("sell-car-form")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="py-14 sm:py-20 bg-primary">
      <Container>
        <div className="flex flex-col items-center text-center gap-6 max-w-xl mx-auto">
          <h2 className="text-2xl sm:text-4xl font-extrabold text-primary-foreground leading-tight">
            Ready to Sell Your Car?
          </h2>
          <p className="text-primary-foreground/80 text-sm sm:text-base">
            Submit your details now or reach out directly — we're happy to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <Button
              onClick={scrollToForm}
              className="bg-primary hover:bg-primary-dark text-white font-bold h-12 px-8 rounded-xl text-sm"
            >
              Submit Your Details
            </Button>
            <a href={`tel:+91${CONTACT.phone}`} className="w-full sm:w-auto">
              <Button
                variant="outline"
                className="w-full border-primary-foreground/40 text-primary-foreground bg-transparent hover:bg-primary-foreground/10 font-semibold h-12 px-6 rounded-xl text-sm gap-2"
              >
                <Phone className="w-4 h-4" /> Call Dealer
              </Button>
            </a>
            <a
              href={`https://wa.me/91${CONTACT.phone}?text=${encodeURIComponent("Hi, I want to sell my car. Please assist.")}`}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full sm:w-auto"
            >
              <Button className="w-full bg-[#25D366] hover:bg-[#20bd5a] text-white font-semibold h-12 px-6 rounded-xl text-sm gap-2">
                <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-5 w-5 invert brightness-0" aria-hidden />
                WhatsApp
              </Button>
            </a>
          </div>
        </div>
      </Container>
    </section>
  );
};

export default SellCarCTA;
