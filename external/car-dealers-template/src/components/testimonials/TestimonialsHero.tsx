import { BUSINESS_NAME, BUSINESS_CITY } from "@/config/business";
import Container from "@/components/Container";

const TestimonialsHero = () => (
  <section className="bg-muted py-14 sm:py-20">
    <Container>
      <div className="max-w-2xl mx-auto text-center space-y-4">
        <span className="inline-block rounded-full bg-primary/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-primary">
          Customer Reviews
        </span>
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-logo-blue">
          What Our Customers Say
        </h1>
        <p className="text-base sm:text-lg text-muted-foreground max-w-xl mx-auto">
          Real feedback from customers who bought or sold their cars through {BUSINESS_NAME} in {BUSINESS_CITY}.
        </p>
      </div>
    </Container>
  </section>
);

export default TestimonialsHero;
