import SiteLayout from "@/components/SiteLayout";
import HeroSection from "@/components/home/HeroSection";
import TrustStripSection from "@/components/home/TrustStripSection";
import FeaturedCarsSection from "@/components/home/FeaturedCarsSection";
import WhyChooseUsSection from "@/components/home/WhyChooseUsSection";
import GallerySection from "@/components/gallery/GallerySection";
import TestimonialsPreviewSection from "@/components/home/TestimonialsPreviewSection";
import LocationCTASection from "@/components/home/LocationCTASection";

const Home = () => {
  return (
    <SiteLayout>
      <HeroSection />
      <TrustStripSection />
      <FeaturedCarsSection />
      <WhyChooseUsSection />
      <GallerySection />
      <TestimonialsPreviewSection />
      <LocationCTASection />
    </SiteLayout>
  );
};

export default Home;
