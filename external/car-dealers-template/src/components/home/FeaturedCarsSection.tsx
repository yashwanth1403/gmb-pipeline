import { Link } from "react-router-dom";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { CONTACT, FEATURED_CAR_IDS } from "@/config/business";
import { Card, CardContent } from "@/components/ui/card";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { Car, CARS, formatPrice } from "@/data/cars";

const FEATURED_CARS: Car[] = FEATURED_CAR_IDS.map((id) =>
  CARS.find((c) => c.id === id),
).filter((c): c is Car => !!c);

const FeaturedCarsSection = () => {
  return (
    <section className="py-12 sm:py-16">
      <Container className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold sm:text-3xl text-logo-blue">
            Featured Cars
          </h2>
          <p className="text-muted-foreground">
            Hand-picked deals ready for you
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {FEATURED_CARS.map((car) => (
            <Card key={car.id} className="overflow-hidden">
              <AspectRatio ratio={16 / 10}>
                <div className="flex h-full w-full items-center justify-center bg-muted overflow-hidden">
                  <img
                    src={car.image}
                    alt={car.name}
                    className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
                  />
                </div>
              </AspectRatio>
              <CardContent className="p-4 space-y-3">
                <div>
                  <h3 className="font-semibold text-base">{car.name}</h3>
                  <p className="text-xs text-muted-foreground">
                    {car.year} · {car.km.toLocaleString("en-IN")} km ·{" "}
                    {car.fuel} · {car.transmission}
                  </p>
                </div>
                <p className="text-xl font-extrabold text-primary">
                  {formatPrice(car.price)}
                </p>
                <div className="flex gap-2">
                  <Button
                    asChild
                    variant="default"
                    size="sm"
                    className="flex-1 text-xs"
                  >
                    <Link to={`/cars/${car.id}`}>View Details</Link>
                  </Button>
                  <Button
                    asChild
                    variant="outline"
                    size="sm"
                    className="flex-1 text-xs border-[#25D366] bg-[#25D366] hover:bg-[#20bd5a] hover:border-[#20bd5a] text-white gap-1.5"
                  >
                    <a
                      href={`https://wa.me/91${CONTACT.phone}?text=${encodeURIComponent(`Hi, I'm interested in ${car.name} (${car.year})`)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-1.5"
                    >
                      <img
                        src="/whatsapp-color-svgrepo-com.svg"
                        alt=""
                        className="h-4 w-4 invert brightness-0"
                        aria-hidden
                      />
                      WhatsApp
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center pt-2">
          <Button asChild variant="secondary" size="lg">
            <Link to="/cars">View All Cars →</Link>
          </Button>
        </div>
      </Container>
    </section>
  );
};

export default FeaturedCarsSection;
