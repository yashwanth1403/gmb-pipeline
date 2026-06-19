import { Link } from "react-router-dom";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { Star, Quote } from "lucide-react";
import { TESTIMONIALS } from "@/data/testimonials";

const TestimonialsPreviewSection = () => {
  const testimonials = TESTIMONIALS.slice(0, 3);
  if (!testimonials.length) return null;

  return (
    <section className="py-16 sm:py-24 bg-white relative overflow-hidden">
      {/* decorative blob */}
      <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-primary/5 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-primary/10 blur-3xl pointer-events-none" />

      <Container className="relative space-y-12">
        <div className="text-center space-y-3">
          <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">
            Customer Reviews
          </p>
          <h2 className="text-3xl font-extrabold sm:text-4xl text-logo-blue">
            What Our Customers Say
          </h2>
          <p className="text-muted-foreground">Real feedback from real buyers</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <div
              key={t.name + i}
              className="relative rounded-2xl border border-border bg-gradient-to-br from-white to-slate-50 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col gap-4"
            >
              {/* quote icon */}
              <Quote className="h-8 w-8 text-primary/20 flex-shrink-0" />

              {/* stars */}
              <div className="flex gap-0.5">
                {Array.from({ length: t.rating }).map((_, j) => (
                  <Star key={j} className="h-4 w-4 fill-logo-blue text-logo-blue-light" />
                ))}
              </div>

              {/* review */}
              <p className="text-sm text-slate-600 leading-relaxed flex-1 italic">
                "{t.review}"
              </p>

              {/* author */}
              <div className="flex items-center gap-3 pt-2 border-t border-border">
                <div className="h-9 w-9 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm flex-shrink-0">
                  {t.name.charAt(0)}
                </div>
                <div>
                  <p className="font-semibold text-sm text-foreground">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.location}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Button asChild variant="outline" size="lg" className="border-primary text-primary hover:bg-primary hover:text-white">
            <Link to="/testimonials">View All Reviews →</Link>
          </Button>
        </div>
      </Container>
    </section>
  );
};

export default TestimonialsPreviewSection;
