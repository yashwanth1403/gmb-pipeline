import {
  MapPin,
  Calendar,
  Gauge,
  Fuel,
  Settings,
  PhoneCall,
} from "lucide-react";
import { formatPrice, formatKm } from "@/data/cars";
import { CONTACT } from "@/config/business";
import React from "react";

interface CarOverviewProps {
  car: {
    name: string;
    price: number;
    year: number;
    km: number;
    fuel: string;
    transmission: string;
    owner: string;
  };
}

export const CarOverview = ({ car }: CarOverviewProps) => {
  const waMessage = encodeURIComponent(
    `Hi, I'm interested in ${car.name} (${car.year}) priced at ${formatPrice(car.price)}. Is it still available?`,
  );
  const waLink = `https://wa.me/91${CONTACT.phone}?text=${waMessage}`;

  return (
    <div className="bg-card rounded-xl border border-border p-5 sm:p-6 shadow-sm flex flex-col gap-6">
      {/* Title */}
      <div>
        <h1 className="text-xl sm:text-2xl font-extrabold text-foreground tracking-tight leading-tight">
          {car.name}
        </h1>
        <p className="text-muted-foreground text-sm mt-1.5 flex items-center gap-1.5 font-medium">
          <MapPin size={15} className="text-primary" /> {CONTACT.address}
        </p>
      </div>

      {/* Price Section */}
      <div>
        <h2 className="text-4xl sm:text-5xl font-extrabold text-primary tracking-tight">
          {formatPrice(car.price)}
        </h2>
        <p className="text-sm text-muted-foreground mt-1.5 font-medium">
          Fixed price, inclusive of all taxes
        </p>
      </div>

      {/* Key Specs Chips */}
      <div className="flex flex-wrap gap-2.5">
        <SpecChip icon={<Calendar size={14} />} label={`${car.year}`} />
        <SpecChip icon={<Gauge size={14} />} label={formatKm(car.km)} />
        <SpecChip icon={<Fuel size={14} />} label={car.fuel} />
        <SpecChip icon={<Settings size={14} />} label={car.transmission} />
        <div className="bg-muted/50 text-foreground px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 border border-border shrink-0">
          {car.owner} Owner
        </div>
      </div>

      {/* Call to Actions */}
      <div className="flex flex-col sm:flex-row gap-3 mt-2">
        <a
          href={waLink}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 bg-[#25D366] hover:bg-[#20bd5a] text-white flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-sm font-bold transition-colors shadow-sm"
        >
          <img src="/whatsapp-color-svgrepo-com.svg" alt="" className="h-5 w-5 invert brightness-0" aria-hidden />
          WhatsApp Dealer
        </a>
        <a
          href={`tel:+91${CONTACT.phone}`}
          className="flex-1 bg-primary hover:bg-primary/90 text-white flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-sm font-bold transition-colors shadow-sm"
        >
          <PhoneCall size={18} />
          Call Dealer
        </a>
      </div>
    </div>
  );
};

const SpecChip = ({
  icon,
  label,
}: {
  icon: React.ReactNode;
  label: string;
}) => (
  <div className="bg-muted/50 text-foreground px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 border border-border shrink-0">
    <span className="text-muted-foreground">{icon}</span>
    {label}
  </div>
);
