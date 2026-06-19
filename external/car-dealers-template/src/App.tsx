import { useEffect } from "react";
import { BUSINESS_NAME, BUSINESS_CITY } from "@/config/business";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Index        from "./pages/Index";
import Cars         from "./pages/Cars";
import CarDetail    from "./pages/CarDetail";
import SellCar      from "./pages/SellCar";
import About        from "./pages/About";
import Testimonials from "./pages/Testimonials";
import Contact      from "./pages/Contact";
import Admin        from "./pages/Admin";
import NotFound     from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  useEffect(() => {
    document.title = `${BUSINESS_NAME} | Trusted Pre-Owned Cars in ${BUSINESS_CITY}`;
  }, []);

  return (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/"             element={<Index />} />
          <Route path="/cars"         element={<Cars />} />
          <Route path="/cars/:slug"   element={<CarDetail />} />
          <Route path="/sell-car"     element={<SellCar />} />
          <Route path="/about"        element={<About />} />
          <Route path="/testimonials" element={<Testimonials />} />
          <Route path="/contact"      element={<Contact />} />

          {/* Admin */}
          <Route path="/admin"        element={<Admin />} />

          {/* Catch-all */}
          <Route path="*"             element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
  );
};

export default App;
