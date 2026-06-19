import inventoryData from "./inventory.json";

export interface Car {
  id: string;
  name: string;
  brand: string;
  model?: string;
  year: number;
  km: number;
  fuel: "Petrol" | "Diesel" | "CNG" | "Electric";
  transmission: "Manual" | "Automatic";
  price: number;
  emi: number;
  image: string;
  images?: string[];
  owner?: string;
  insurance?: string;
  description?: string;
}

export const CARS: Car[] = inventoryData as Car[];

export function getCarById(id: string): Car | undefined {
  return CARS.find((c) => c.id === id);
}

// Derived dynamically so they always reflect the actual inventory
export const BRANDS       = ["All", ...Array.from(new Set(CARS.map((c) => c.brand))).sort()];
export const FUEL_TYPES   = ["All", "Petrol", "Diesel", "CNG", "Electric"];
export const TRANSMISSIONS = ["All", "Manual", "Automatic"];
export const YEARS        = [
  "All",
  ...Array.from(new Set(CARS.map((c) => String(c.year))))
    .sort((a, b) => Number(b) - Number(a)),
];

export function formatPrice(price: number): string {
  if (price >= 100000) {
    return `₹${(price / 100000).toFixed(1)}L`;
  }
  return `₹${price.toLocaleString("en-IN")}`;
}

export function formatKm(km: number): string {
  return `${km.toLocaleString("en-IN")} km`;
}
