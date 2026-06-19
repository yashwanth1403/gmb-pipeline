import React from "react";

interface CarSpecsProps {
  car: {
    brand: string;
    model: string;
    year: number;
    fuel: string;
    transmission: string;
    km: number;
    owner: string;
    insurance: string;
  };
}

export const CarSpecs = ({ car }: CarSpecsProps) => {
  const specs = [
    { label: "Brand", value: car.brand },
    { label: "Model", value: car.model },
    { label: "Year", value: car.year.toString() },
    { label: "Fuel Type", value: car.fuel },
    { label: "Transmission", value: car.transmission },
    { label: "KM Driven", value: `${car.km.toLocaleString("en-IN")} km` },
    { label: "Ownership", value: `${car.owner} Owner` },
    { label: "Registration", value: "Telangana (TS)" },
    { label: "Insurance", value: car.insurance },
  ];

  return (
    <div className="bg-card rounded-xl border border-border p-5 sm:p-6 shadow-sm overflow-hidden">
      <h2 className="text-xl font-bold text-logo-blue mb-6 flex items-center gap-2">
        <span className="w-1.5 h-6 bg-primary rounded-full inline-block"></span>
        Key Specifications
      </h2>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-y-6 gap-x-6 sm:gap-x-12">
        {specs.map((spec, idx) => (
          <div
            key={idx}
            className="flex flex-col gap-1 border-l-2 border-border pl-3"
          >
            <span className="text-xs text-muted-foreground font-semibold uppercase tracking-wider">
              {spec.label}
            </span>
            <span className="text-sm sm:text-base font-bold text-foreground">
              {spec.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
