import { useParams, Navigate } from "react-router-dom";
import SiteLayout from "@/components/SiteLayout";
import Container from "@/components/Container";
import { CarGallery } from "@/components/car-detail/CarGallery";
import { CarOverview } from "@/components/car-detail/CarOverview";
import { CarSpecs } from "@/components/car-detail/CarSpecs";
import { CarDescription } from "@/components/car-detail/CarDescription";
import { EMICalculator } from "@/components/car-detail/EMICalculator";
import { SimilarCars } from "@/components/car-detail/SimilarCars";
import { StickyContactBar } from "@/components/car-detail/StickyContactBar";
import { useEffect } from "react";
import { getCarById } from "@/data/cars";

const CarDetail = () => {
  const { slug } = useParams<{ slug: string }>();
  const car = slug ? getCarById(slug) : undefined;

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [slug]);

  if (!car) {
    return <Navigate to="/cars" replace />;
  }

  const carForOverview = {
    name: car.name,
    price: car.price,
    year: car.year,
    km: car.km,
    fuel: car.fuel,
    transmission: car.transmission,
    owner: car.owner ?? "1st",
  };

  const carForSpecs = {
    brand: car.brand,
    model: car.model ?? (car.name.replace(car.brand, "").trim() || car.name),
    year: car.year,
    fuel: car.fuel,
    transmission: car.transmission,
    km: car.km,
    owner: car.owner ?? "1st",
    insurance: car.insurance ?? "Third Party",
  };

  const galleryImages = car.images && car.images.length > 0 ? car.images : [car.image];
  const description = car.description ?? `${car.name} - well maintained pre-owned car. Contact us for more details and viewing.`;

  return (
    <SiteLayout>
      <div className="bg-muted/20 min-h-[calc(100vh-64px)] pb-32 lg:pb-16 pt-4 sm:pt-6">
        <Container>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
            <div className="lg:col-span-7 xl:col-span-8 flex flex-col gap-6 lg:gap-8">
              <CarGallery images={galleryImages} />

              <div className="lg:hidden">
                <CarOverview car={carForOverview} />
              </div>

              <CarSpecs car={carForSpecs} />
              <CarDescription description={description} />
              <EMICalculator carPrice={car.price} />
            </div>

            <div className="hidden lg:block lg:col-span-5 xl:col-span-4">
              <div className="sticky top-24">
                <CarOverview car={carForOverview} />
              </div>
            </div>
          </div>

          <div className="mt-10 lg:mt-16">
            <SimilarCars currentCarId={car.id} />
          </div>
        </Container>

        <StickyContactBar />
      </div>
    </SiteLayout>
  );
};

export default CarDetail;
