import Container from "@/components/Container";
import { ShieldCheck, FileCheck, Gauge, ClipboardList } from "lucide-react";

const PILLARS = [
  { icon: ShieldCheck,    label: "Non-Accident Cars",       sub: "Every car inspected" },
  { icon: FileCheck,      label: "3-Day RC Transfer",        sub: "Ownership guaranteed" },
  { icon: Gauge,          label: "Odometer Verified",        sub: "No tampering, ever" },
  { icon: ClipboardList,  label: "Service History Check",    sub: "Full records reviewed" },
];

const TrustStripSection = () => (
  <section className="bg-white border-b border-border">
    <Container>
      <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-y md:divide-y-0 divide-border">
        {PILLARS.map(({ icon: Icon, label, sub }) => (
          <div key={label} className="flex items-center gap-3 px-4 py-4 sm:py-5">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="text-sm font-bold text-foreground leading-tight">{label}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>
            </div>
          </div>
        ))}
      </div>
    </Container>
  </section>
);

export default TrustStripSection;
