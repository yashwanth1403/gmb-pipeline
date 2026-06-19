import { Star } from "lucide-react";

interface TestimonialCardProps {
  name: string;
  location: string;
  review: string;
  car: string;
  rating: number;
}

const TestimonialCard = ({ name, location, review, car, rating }: TestimonialCardProps) => (
  <div className="bg-card rounded-xl shadow-sm border border-border p-6 flex flex-col gap-4 h-full">
    {/* Quote icon */}
    <svg className="h-7 w-7 text-logo-blue-light opacity-70" fill="currentColor" viewBox="0 0 32 32" aria-hidden="true">
      <path d="M9.352 4C4.456 7.456 1 13.12 1 19.36c0 5.088 3.072 8.064 6.624 8.064 3.36 0 5.856-2.688 5.856-5.856 0-3.168-2.208-5.472-5.088-5.472-.576 0-1.344.096-1.536.192.48-3.264 3.552-7.104 6.624-9.024L9.352 4zm16.512 0c-4.8 3.456-8.256 9.12-8.256 15.36 0 5.088 3.072 8.064 6.624 8.064 3.264 0 5.856-2.688 5.856-5.856 0-3.168-2.304-5.472-5.184-5.472-.576 0-1.248.096-1.44.192.48-3.264 3.456-7.104 6.528-9.024L25.864 4z" />
    </svg>

    {/* Review */}
    <p className="text-sm text-muted-foreground leading-relaxed flex-1">"{review}"</p>

    {/* Stars */}
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star key={i} className={`h-4 w-4 ${i < rating ? "fill-logo-blue text-logo-blue-light" : "fill-muted text-muted"}`} />
      ))}
    </div>

    {/* Author */}
    <div className="border-t border-border pt-4">
      <p className="font-bold text-sm text-foreground">{name}</p>
      <p className="text-xs text-muted-foreground">{location}</p>
      <p className="text-xs text-primary font-medium mt-0.5">Bought: {car}</p>
    </div>
  </div>
);

export default TestimonialCard;
