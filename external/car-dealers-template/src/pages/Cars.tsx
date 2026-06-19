import { useState, useMemo } from "react";
import SiteLayout from "@/components/SiteLayout";
import Container from "@/components/Container";
import CarCard from "@/components/cars/CarCard";
import { FilterPanel, Filters, DEFAULT_FILTERS } from "@/components/cars/FilterSidebar";
import { CARS } from "@/data/cars";
import { SlidersHorizontal, X, Car } from "lucide-react";

const PAGE_SIZE = 6;

const Cars = () => {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const filtered = useMemo(() => {
    let list = [...CARS];

    if (filters.brand !== "All") list = list.filter((c) => c.brand === filters.brand);
    if (filters.fuel !== "All") list = list.filter((c) => c.fuel === filters.fuel);
    if (filters.transmission !== "All")
      list = list.filter((c) => c.transmission === filters.transmission);
    if (filters.year !== "All") list = list.filter((c) => String(c.year) === filters.year);
    list = list.filter((c) => c.price >= filters.priceMin && c.price <= filters.priceMax);

    if (filters.sort === "price_asc") list.sort((a, b) => a.price - b.price);
    else if (filters.sort === "price_desc") list.sort((a, b) => b.price - a.price);
    else if (filters.sort === "newest") list.sort((a, b) => b.year - a.year);
    else if (filters.sort === "km_asc") list.sort((a, b) => a.km - b.km);

    return list;
  }, [filters]);

  const visible = filtered.slice(0, visibleCount);
  const hasMore = visibleCount < filtered.length;

  const handleClear = () => {
    setFilters(DEFAULT_FILTERS);
    setVisibleCount(PAGE_SIZE);
  };

  const activeFilterCount = [
    filters.brand !== "All",
    filters.fuel !== "All",
    filters.transmission !== "All",
    filters.year !== "All",
    filters.priceMax < 6000000,
  ].filter(Boolean).length;

  return (
    <SiteLayout>
      {/* Page Header */}
      <div className="bg-primary py-10">
        <Container>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-primary-foreground tracking-tight">
            Available Cars
          </h1>
          <p className="text-primary-foreground/70 mt-1 text-sm sm:text-base">
            Verified pre-owned cars available in Hyderabad
          </p>
          <p className="mt-3 inline-flex items-center gap-1.5 bg-secondary text-secondary-foreground text-xs font-bold px-3 py-1.5 rounded-full">
            <Car size={13} />
            {filtered.length} Cars Available
          </p>
        </Container>
      </div>

      <Container className="py-8">
        <div className="flex gap-8">
          {/* ── Desktop Sidebar ── */}
          <aside className="hidden lg:block w-64 shrink-0">
            <div className="sticky top-24 bg-card border border-border rounded-xl p-5 shadow-sm">
              <FilterPanel
                filters={filters}
                onChange={(f) => { setFilters(f); setVisibleCount(PAGE_SIZE); }}
                onClear={handleClear}
              />
            </div>
          </aside>

          {/* ── Main Content ── */}
          <div className="flex-1 min-w-0">
            {/* Mobile filter bar */}
            <div className="flex items-center justify-between gap-3 mb-5 lg:hidden">
              <button
                onClick={() => setSheetOpen(true)}
                className="flex items-center gap-2 h-11 px-4 rounded-xl border border-border bg-card text-foreground text-sm font-semibold hover:border-primary transition-colors"
              >
                <SlidersHorizontal size={16} />
                Filters
                {activeFilterCount > 0 && (
                  <span className="bg-secondary text-secondary-foreground text-xs font-bold px-1.5 py-0.5 rounded-full">
                    {activeFilterCount}
                  </span>
                )}
              </button>
              <p className="text-sm text-muted-foreground font-medium">
                {filtered.length} results
              </p>
            </div>

            {/* Grid or Empty State */}
            {visible.length === 0 ? (
              <EmptyState onClear={handleClear} />
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                  {visible.map((car) => (
                    <CarCard key={car.id} car={car} />
                  ))}
                </div>

                {/* Load More */}
                {hasMore && (
                  <div className="mt-10 flex justify-center">
                    <button
                      onClick={() => setVisibleCount((v) => v + PAGE_SIZE)}
                      className="h-12 px-10 bg-primary text-primary-foreground rounded-xl font-semibold text-sm hover:bg-primary-dark transition-colors"
                    >
                      Load More Cars
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </Container>

      {/* ── Mobile Filter Sheet ── */}
      {sheetOpen && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end lg:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-foreground/50"
            onClick={() => setSheetOpen(false)}
          />
          {/* Sheet */}
          <div className="relative bg-card rounded-t-2xl px-5 pt-5 pb-8 max-h-[85vh] overflow-y-auto shadow-xl menu-slide-in">
            <div className="mx-auto w-10 h-1 bg-muted rounded-full mb-5" />
            <FilterPanel
              filters={filters}
              onChange={(f) => { setFilters(f); setVisibleCount(PAGE_SIZE); }}
              onClear={handleClear}
              onClose={() => setSheetOpen(false)}
              isMobileSheet
            />
          </div>
        </div>
      )}
    </SiteLayout>
  );
};

/* ── Empty State ── */
const EmptyState = ({ onClear }: { onClear: () => void }) => (
  <div className="flex flex-col items-center justify-center py-24 text-center gap-5">
    <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center">
      <Car size={36} className="text-muted-foreground" />
    </div>
    <div>
      <h3 className="text-lg font-bold text-foreground">No cars match your filters</h3>
      <p className="text-muted-foreground text-sm mt-1">
        Try adjusting or clearing your filters to see more results.
      </p>
    </div>
    <button
      onClick={onClear}
      className="flex items-center gap-2 h-11 px-6 bg-primary text-primary-foreground rounded-xl text-sm font-semibold hover:bg-primary-dark transition-colors"
    >
      <X size={15} />
      Clear Filters
    </button>
  </div>
);

export default Cars;
