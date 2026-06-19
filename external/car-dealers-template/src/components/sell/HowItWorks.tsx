import { ClipboardList, PhoneCall, BadgeIndianRupee } from "lucide-react";
import { BUSINESS_NAME } from "@/config/business";
import Container from "@/components/Container";

const getSteps = () => [
  { icon: ClipboardList,     step: "01", title: "Submit Car Details",    description: "Fill in your car info and contact details. Takes less than 60 seconds.",                          accent: "from-logo-blue to-primary" },
  { icon: PhoneCall,         step: "02", title: "Our Team Contacts You", description: `A ${BUSINESS_NAME} executive will call or WhatsApp you within 2 hours.`,                         accent: "from-blue-500 to-blue-600" },
  { icon: BadgeIndianRupee,  step: "03", title: "Get Best Price Offer",  description: "Receive a fair, transparent price offer with no hidden deductions.",                             accent: "from-blue-400 to-blue-500" },
];

const HowItWorks = () => {
  const steps = getSteps();
  return (
    <section className="py-16 sm:py-24 bg-white">
      <Container>
        <div className="text-center space-y-3 mb-14">
          <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">Simple process</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-logo-blue">How It Works</h2>
        </div>

        <div className="relative grid grid-cols-1 sm:grid-cols-3 gap-8">
          {/* connector line desktop */}
          <div className="hidden sm:block absolute top-10 left-[calc(16.67%+2rem)] right-[calc(16.67%+2rem)] h-0.5 bg-gradient-to-r from-secondary via-blue-500 to-blue-600 opacity-40" />

          {steps.map(({ icon: Icon, step, title, description, accent }) => (
            <div key={step} className="relative flex flex-col items-center text-center gap-5">
              {/* step badge */}
              <div className={`relative z-10 w-20 h-20 rounded-2xl bg-gradient-to-br ${accent} flex flex-col items-center justify-center shadow-xl`}>
                <Icon className="w-8 h-8 text-white" />
                <span className="text-[10px] font-bold text-white/70 mt-0.5">{step}</span>
              </div>

              <div className="space-y-1.5">
                <h3 className="font-bold text-foreground text-base">{title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed max-w-[220px] mx-auto">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
};

export default HowItWorks;
