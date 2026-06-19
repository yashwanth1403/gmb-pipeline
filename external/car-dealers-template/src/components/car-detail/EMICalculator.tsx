import { useState, useMemo } from "react";
import { formatPrice } from "@/data/cars";
import { Calculator } from "lucide-react";

interface EMICalculatorProps {
  carPrice: number;
}

export const EMICalculator = ({ carPrice }: EMICalculatorProps) => {
  const [downPayment, setDownPayment] = useState(Math.round(carPrice * 0.2));
  const [interestRate, setInterestRate] = useState(9.5);
  const [tenure, setTenure] = useState(60); // months

  const emi = useMemo(() => {
    const principal = carPrice - downPayment;
    const ratePerMonth = interestRate / 12 / 100;

    if (principal <= 0) return 0;
    if (ratePerMonth === 0) return Math.round(principal / tenure);

    const calculatedEmi =
      (principal * ratePerMonth * Math.pow(1 + ratePerMonth, tenure)) /
      (Math.pow(1 + ratePerMonth, tenure) - 1);

    return Math.round(calculatedEmi);
  }, [carPrice, downPayment, interestRate, tenure]);

  return (
    <div className="bg-card rounded-xl border border-border p-5 sm:p-6 shadow-sm overflow-hidden">
      <h2 className="text-xl font-bold text-logo-blue mb-6 flex items-center gap-2">
        <span className="w-1.5 h-6 bg-primary rounded-full inline-block"></span>
        <Calculator className="text-primary mb-0.5" size={20} />
        EMI Calculator
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-8 items-center">
        <div className="md:col-span-3 space-y-6">
          {/* Down Payment */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="text-sm font-bold text-muted-foreground uppercase tracking-wide">
                Down Payment
              </label>
              <div className="bg-muted px-3 py-1 rounded-md text-sm font-bold border border-border">
                {formatPrice(downPayment)}
              </div>
            </div>
            <input
              type="range"
              min={0}
              max={carPrice}
              step={10000}
              value={downPayment}
              onChange={(e) => setDownPayment(Number(e.target.value))}
              className="w-full accent-primary h-2 bg-muted rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Interest Rate */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="text-sm font-bold text-muted-foreground uppercase tracking-wide">
                Interest Rate
              </label>
              <div className="bg-muted px-3 py-1 rounded-md text-sm font-bold border border-border">
                {interestRate}%{" "}
                <span className="text-xs font-normal text-muted-foreground">
                  p.a.
                </span>
              </div>
            </div>
            <input
              type="range"
              min={7}
              max={15}
              step={0.1}
              value={interestRate}
              onChange={(e) => setInterestRate(Number(e.target.value))}
              className="w-full accent-primary h-2 bg-muted rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Tenure */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="text-sm font-bold text-muted-foreground uppercase tracking-wide">
                Loan Tenure
              </label>
              <div className="bg-muted px-3 py-1 rounded-md text-sm font-bold border border-border">
                {tenure / 12} Years
              </div>
            </div>
            <input
              type="range"
              min={12}
              max={84}
              step={12}
              value={tenure}
              onChange={(e) => setTenure(Number(e.target.value))}
              className="w-full accent-primary h-2 bg-muted rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>

        {/* Amount Display */}
        <div className="md:col-span-2 bg-primary/5 rounded-2xl p-6 border-2 border-primary/20 flex flex-col items-center justify-center text-center shadow-inner h-full">
          <p className="text-sm font-bold text-primary uppercase tracking-widest mb-2">
            Your EMI
          </p>
          <div className="flex items-baseline gap-1">
            <p className="text-4xl lg:text-5xl font-extrabold text-foreground tracking-tight">
              ₹{emi.toLocaleString("en-IN")}
            </p>
            <p className="text-base text-muted-foreground font-semibold">/mo</p>
          </div>
          <p className="text-xs text-muted-foreground mt-4 font-medium opacity-80 leading-relaxed max-w-[200px]">
            *Estimated. Exact EMI varies by bank and profile.
          </p>
        </div>
      </div>
    </div>
  );
};
