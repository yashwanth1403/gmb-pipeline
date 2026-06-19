import testimonialsData from "./testimonials.json";

export interface Testimonial {
  name: string;
  location: string;
  review: string;
  car: string;
  rating: number;
}

export const TESTIMONIALS: Testimonial[] = testimonialsData;
