/**
 * Admin car inventory – mock data for dashboard.
 * No backend yet; uses local state.
 */

export type CarStatus = "Available" | "Sold";

export interface AdminCar {
  id: string;
  name: string;
  brand: string;
  year: number;
  km: number;
  fuel: "Petrol" | "Diesel" | "CNG" | "Electric";
  transmission: "Manual" | "Automatic";
  price: number;
  emi?: number;
  description?: string;
  image: string;
  images?: string[];
  status: CarStatus;
}

export const INITIAL_ADMIN_CARS: AdminCar[] = [
  {
    id: "1",
    name: "BMW 3 Series 330i",
    brand: "BMW",
    year: 2021,
    km: 28000,
    fuel: "Petrol",
    transmission: "Automatic",
    price: 3850000,
    emi: 45000,
    status: "Available",
    image: "/images/BMW-3-Series.jpg",
  },
  {
    id: "2",
    name: "Maruti Swift ZXi",
    brand: "Maruti",
    year: 2020,
    km: 42000,
    fuel: "Petrol",
    transmission: "Manual",
    price: 620000,
    emi: 7200,
    status: "Available",
    image: "/images/Maruthi Swift vxi.avif",
  },
  {
    id: "3",
    name: "Honda City VX CVT",
    brand: "Honda",
    year: 2022,
    km: 18000,
    fuel: "Petrol",
    transmission: "Automatic",
    price: 1150000,
    emi: 13500,
    status: "Sold",
    image: "/images/Honda City ZX.jpg",
  },
  {
    id: "4",
    name: "Toyota Innova Crysta G",
    brand: "Toyota",
    year: 2019,
    km: 65000,
    fuel: "Diesel",
    transmission: "Manual",
    price: 1650000,
    emi: 19000,
    status: "Available",
    image: "/images/Toyota Innova Crysta G.jpeg",
  },
  {
    id: "5",
    name: "Mercedes-Benz C 200",
    brand: "Mercedes-Benz",
    year: 2022,
    km: 18000,
    fuel: "Petrol",
    transmission: "Automatic",
    price: 4250000,
    emi: 49500,
    status: "Available",
    image: "/images/Mercedes-Benz-C-Class.jpg",
  },
  {
    id: "6",
    name: "Kia Seltos HTX G",
    brand: "Kia",
    year: 2021,
    km: 35000,
    fuel: "Petrol",
    transmission: "Automatic",
    price: 1280000,
    emi: 15000,
    status: "Available",
    image: "/images/Kia Seltos HTX G.jpg",
  },
  {
    id: "7",
    name: "Maruti Ertiga VDI",
    brand: "Maruti",
    year: 2020,
    km: 55000,
    fuel: "Diesel",
    transmission: "Manual",
    price: 870000,
    emi: 10200,
    status: "Sold",
    image: "/images/Maruti Ertiga VDI.avif",
  },
  {
    id: "8",
    name: "Hyundai Creta SX",
    brand: "Hyundai",
    year: 2023,
    km: 12000,
    fuel: "Petrol",
    transmission: "Automatic",
    price: 1540000,
    emi: 18000,
    status: "Available",
    image: "/images/Hyundai Creta SX.jpg",
  },
];
