import { BadgeIndianRupee, Zap, MessageCircle, FileCheck } from "lucide-react";
import { BUSINESS_NAME } from "@/config/business";
import Container from "@/components/Container";

const benefits = [
  { icon: BadgeIndianRupee, title: "Best Price Evaluation",  description: "We assess your car fairly and offer the best market price.",           accent: "from-logo-blue to-primary" },
  { icon: Zap,              title: "Quick Response",         description: "Our team will contact you within 2 hours of submission.",               accent: "from-blue-500 to-blue-600" },
  { icon: MessageCircle,    title: "Instant WhatsApp",       description: "Communicate directly via WhatsApp for quick updates.",                   accent: "from-blue-400 to-blue-500" },
  { icon: FileCheck,        title: "Hassle-Free RC Transfer",description: "We handle all paperwork and RC transfer formalities.",                   accent: "from-blue-700 to-blue-800" },
];

const SellCarBenefits = () => (
  <section className="py-16 sm:py-24 bg-[#0f172a] relative overflow-hidden">
    <div
      className="absolute inset-0 opacity-[0.04]"
      style={{ backgroundImage: "linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)", backgroundSize: "40px 40px" }}
      aria-hidden
    />
    <Container className="relative space-y-12">
      <div className="text-center space-y-3">
        <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">Sell with confidence</p>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white">Why Sell With {BUSINESS_NAME}?</h2>
        <p className="text-slate-400 max-w-md mx-auto">Get the best value for your car with zero hassle</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {benefits.map((b, i) => (
          <div
            key={b.title}
            className="relative rounded-2xl bg-white/5 border border-white/10 p-6 flex flex-col gap-4 hover:bg-white/10 hover:-translate-y-1 transition-all duration-300"
          >
            <span className="absolute top-4 right-4 text-4xl font-black text-white/5 select-none leading-none">
              {String(i + 1).padStart(2, "0")}
            </span>
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${b.accent} flex items-center justify-center shadow-lg`}>
              <b.icon className="h-6 w-6 text-white" />
            </div>
            <div className="space-y-1.5">
              <h3 className="font-bold text-white text-base">{b.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{b.description}</p>
            </div>
          </div>
        ))}
      </div>
    </Container>
  </section>
);

export default SellCarBenefits;
