import SiteLayout from "@/components/SiteLayout";
import AboutHero from "@/components/about/AboutHero";
import OurStory from "@/components/about/OurStory";
import TrustFeatures from "@/components/about/TrustFeatures";
import BusinessHighlights from "@/components/about/BusinessHighlights";
import AboutCTA from "@/components/about/AboutCTA";

const About = () => (
  <SiteLayout>
    <AboutHero />
    <OurStory />
    <TrustFeatures />
    <BusinessHighlights />
    <AboutCTA />
  </SiteLayout>
);

export default About;
