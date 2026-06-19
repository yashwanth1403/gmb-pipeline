import { X } from "lucide-react";
import { BRANDS, FUEL_TYPES, TRANSMISSIONS, YEARS } from "@/data/cars";

export interface Filters {
  brand: string;
  fuel: string;
  transmission: string;
  year: string;
  priceMin: number;
  priceMax: number;
  sort: string;
}

export const DEFAULT_FILTERS: Filters = {
  brand: "All",
  fuel: "All",
  transmission: "All",
  year: "All",
  priceMin: 0,
  priceMax: 6000000,
  sort: "newest",
};

interface FilterPanelProps {
  filters: Filters;
  onChange: (f: Filters) => void;
  onClear: () => void;
  onClose?: () => void;
  isMobileSheet?: boolean;
}

const SORT_OPTIONS = [
  { value: "newest", label: "Newest First" },
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "km_asc", label: "KM: Low to High" },
];

export const FilterPanel = ({
  filters,
  onChange,
  onClear,
  onClose,
  isMobileSheet = false,
}: FilterPanelProps) => {
  const set = (key: keyof Filters, value: string | number) =>
    onChange({ ...filters, [key]: value });

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="font-bold text-logo-blue text-base">Filters</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={onClear}
            className="text-xs text-logo-blue-light font-semibold hover:underline"
          >
            Clear All
          </button>
          {isMobileSheet && onClose && (
            <button
              onClick={onClose}
              className="ml-2 p-1 rounded-md hover:bg-muted"
              aria-label="Close filters"
            >
              <X size={18} className="text-foreground" />
            </button>
          )}
        </div>
      </div>

      {/* Sort */}
      <FilterGroup label="Sort By">
        <select
          value={filters.sort}
          onChange={(e) => set("sort", e.target.value)}
          className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </FilterGroup>

      {/* Price Range */}
      <FilterGroup label={`Price Range: ₹${(filters.priceMin / 100000).toFixed(0)}L – ₹${(filters.priceMax / 100000).toFixed(0)}L`}>
        <div className="space-y-2">
          <input
            type="range"
            min={0}
            max={6000000}
            step={50000}
            value={filters.priceMax}
            onChange={(e) => set("priceMax", Number(e.target.value))}
            className="w-full accent-primary h-2 rounded-full cursor-pointer"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>₹0</span>
            <span>₹60L</span>
          </div>
        </div>
      </FilterGroup>

      {/* Brand */}
      <FilterGroup label="Brand">
        <ChipGroup
          options={BRANDS}
          value={filters.brand}
          onChange={(v) => set("brand", v)}
        />
      </FilterGroup>

      {/* Fuel */}
      <FilterGroup label="Fuel Type">
        <ChipGroup
          options={FUEL_TYPES}
          value={filters.fuel}
          onChange={(v) => set("fuel", v)}
        />
      </FilterGroup>

      {/* Transmission */}
      <FilterGroup label="Transmission">
        <ChipGroup
          options={TRANSMISSIONS}
          value={filters.transmission}
          onChange={(v) => set("transmission", v)}
        />
      </FilterGroup>

      {/* Year */}
      <FilterGroup label="Model Year">
        <select
          value={filters.year}
          onChange={(e) => set("year", e.target.value)}
          className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
        >
          {YEARS.map((y) => (
            <option key={y} value={y}>
              {y === "All" ? "All Years" : y}
            </option>
          ))}
        </select>
      </FilterGroup>

      {/* Mobile apply button */}
      {isMobileSheet && onClose && (
        <button
          onClick={onClose}
          className="w-full h-12 bg-primary text-primary-foreground rounded-xl font-semibold text-sm hover:bg-primary-dark transition-colors mt-2"
        >
          Apply Filters
        </button>
      )}
    </div>
  );
};

const FilterGroup = ({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) => (
  <div className="space-y-2">
    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
      {label}
    </p>
    {children}
  </div>
);

const ChipGroup = ({
  options,
  value,
  onChange,
}: {
  options: string[];
  value: string;
  onChange: (v: string) => void;
}) => (
  <div className="flex flex-wrap gap-2">
    {options.map((opt) => (
      <button
        key={opt}
        onClick={() => onChange(opt)}
        className={`px-3 h-8 rounded-full text-xs font-medium border transition-colors ${
          value === opt
            ? "bg-primary text-primary-foreground border-primary"
            : "bg-background text-foreground border-border hover:border-primary hover:text-primary"
        }`}
      >
        {opt}
      </button>
    ))}
  </div>
);
