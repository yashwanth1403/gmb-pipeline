import SiteLayout from "@/components/SiteLayout";
import TestimonialsHero from "@/components/testimonials/TestimonialsHero";
import TestimonialsGrid from "@/components/testimonials/TestimonialsGrid";
import RatingHighlight from "@/components/testimonials/RatingHighlight";
import TestimonialsCTA from "@/components/testimonials/TestimonialsCTA";

const Testimonials = () => (
  <SiteLayout>
    <TestimonialsHero />
    <TestimonialsGrid />
    <RatingHighlight />
    <TestimonialsCTA />
  </SiteLayout>
);

export default Testimonials;
