import Container from "@/components/Container";
import { ShieldCheck, BadgeIndianRupee, Handshake, Car, FileCheck } from "lucide-react";

const FEATURES = [
  { icon: BadgeIndianRupee, title: "Transparent Pricing",     desc: "No hidden charges. The price you see is what you pay — no surprises.",          accent: "from-blue-400 to-blue-500" },
  { icon: ShieldCheck,      title: "Verified Pre-Owned Cars", desc: "Multi-point inspection on every car before it's listed for sale.",               accent: "from-blue-500 to-blue-600" },
  { icon: Handshake,        title: "Loan Assistance",         desc: "We connect you with trusted banks and NBFCs for hassle-free financing.",          accent: "from-logo-blue to-primary" },
  { icon: Car,              title: "Insurance Support",       desc: "Comprehensive or third-party insurance arranged before you drive away.",           accent: "from-blue-700 to-blue-800" },
  { icon: FileCheck,        title: "RC Transfer Support",     desc: "We handle all paperwork and RC transfer so you don't have to worry.",             accent: "from-blue-500 to-blue-600" },
];

const TrustFeatures = () => (
  <section className="py-16 sm:py-24 bg-[#0f172a] relative overflow-hidden">
    <div
      className="absolute inset-0 opacity-[0.04]"
      style={{ backgroundImage: "linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px)", backgroundSize: "40px 40px" }}
      aria-hidden
    />
    <Container className="relative space-y-12">
      <div className="text-center space-y-3">
        <p className="text-sm font-semibold tracking-widest text-logo-blue-light uppercase">Our promise</p>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white">Why Customers Trust Us</h2>
        <p className="text-slate-400 max-w-md mx-auto">Everything you need for a smooth, stress-free car buying experience</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        {FEATURES.map((f, i) => (
          <div
            key={f.title}
            className="relative rounded-2xl bg-white/5 border border-white/10 p-6 flex flex-col gap-4 hover:bg-white/10 hover:-translate-y-1 transition-all duration-300"
          >
            <span className="absolute top-4 right-4 text-4xl font-black text-white/5 select-none leading-none">
              {String(i + 1).padStart(2, "0")}
            </span>
            <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${f.accent} flex items-center justify-center shadow-lg`}>
              <f.icon className="h-5 w-5 text-white" />
            </div>
            <div className="space-y-1">
              <h3 className="font-bold text-white text-sm leading-snug">{f.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </Container>
  </section>
);

export default TrustFeatures;
