import { BUSINESS_CITY } from "@/config/business";
import { TESTIMONIALS } from "@/data/testimonials";
import Container from "@/components/Container";
import TestimonialCard from "./TestimonialCard";

const TestimonialsGrid = () => (
  <section className="py-14 sm:py-20 bg-background">
    <Container className="space-y-10">
      <div className="text-center space-y-2">
        <h2 className="text-2xl sm:text-3xl font-extrabold text-logo-blue">Customer Experiences</h2>
        <p className="text-muted-foreground">Trusted by buyers and sellers across {BUSINESS_CITY}</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {TESTIMONIALS.map((t) => (
          <TestimonialCard key={t.name} {...t} />
        ))}
      </div>
    </Container>
  </section>
);

export default TestimonialsGrid;
