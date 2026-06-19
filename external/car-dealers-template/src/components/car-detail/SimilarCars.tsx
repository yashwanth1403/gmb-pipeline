import React from "react";
import { Link } from "react-router-dom";
import CarCard from "@/components/cars/CarCard";
import { CARS } from "@/data/cars";

interface SimilarCarsProps {
  currentCarId?: string;
}

export const SimilarCars = ({ currentCarId }: SimilarCarsProps) => {
  const recommendedCars = CARS.filter((c) => c.id !== currentCarId).slice(0, 4);

  return (
    <div className="py-6 sm:py-8 mt-4 border-t border-border/60">
      <div className="flex justify-between items-center mb-6 sm:mb-8">
        <h2 className="text-2xl font-extrabold text-logo-blue tracking-tight">
          Similar Cars You May Like
        </h2>
        <Link to="/cars" className="text-sm font-bold text-primary hover:underline underline-offset-4 hidden sm:block">
          View All Inventory
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {recommendedCars.map((car) => (
          <CarCard key={car.id} car={car} />
        ))}
      </div>

      <Link to="/cars" className="block w-full mt-6 py-3.5 rounded-xl border-2 border-primary text-primary font-bold hover:bg-primary/5 transition-colors sm:hidden text-center">
        View All Inventory
      </Link>
    </div>
  );
};
