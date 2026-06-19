import SiteLayout from "@/components/SiteLayout";
import SellCarHero from "@/components/sell/SellCarHero";
import SellCarBenefits from "@/components/sell/SellCarBenefits";
import SellCarForm from "@/components/sell/SellCarForm";
import HowItWorks from "@/components/sell/HowItWorks";
import SellCarCTA from "@/components/sell/SellCarCTA";

const SellCar = () => (
  <SiteLayout>
    <SellCarHero />
    <SellCarBenefits />
    <SellCarForm />
    <HowItWorks />
    <SellCarCTA />
  </SiteLayout>
);

export default SellCar;
