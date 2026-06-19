import { useState } from "react";
import { Upload } from "lucide-react";
import Container from "@/components/Container";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";

const BRANDS = ["BMW", "Mercedes-Benz", "Hyundai", "Maruti", "Honda", "Toyota", "Tata", "Kia", "Mahindra", "Renault", "Volkswagen", "Skoda", "MG", "Ford", "Other"];
const YEARS = Array.from({ length: 15 }, (_, i) => String(new Date().getFullYear() - i));
const FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric", "Hybrid"];
const TRANSMISSIONS = ["Manual", "Automatic"];

interface FormData {
  name: string;
  phone: string;
  brand: string;
  model: string;
  year: string;
  km: string;
  fuel: string;
  transmission: string;
  expectedPrice: string;
}

interface Errors {
  name?: string;
  phone?: string;
  brand?: string;
  model?: string;
  year?: string;
  km?: string;
  fuel?: string;
  transmission?: string;
}

const SellCarForm = () => {
  const { toast } = useToast();
  const [form, setForm] = useState<FormData>({
    name: "", phone: "", brand: "", model: "", year: "",
    km: "", fuel: "", transmission: "", expectedPrice: "",
  });
  const [errors, setErrors] = useState<Errors>({});
  const [submitted, setSubmitted] = useState(false);

  const set = (field: keyof FormData, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }));
    if (errors[field as keyof Errors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validate = (): boolean => {
    const e: Errors = {};
    if (!form.name.trim()) e.name = "Full name is required.";
    if (!/^[6-9]\d{9}$/.test(form.phone)) e.phone = "Enter a valid 10-digit Indian mobile number.";
    if (!form.brand) e.brand = "Please select a brand.";
    if (!form.model.trim()) e.model = "Car model is required.";
    if (!form.year) e.year = "Please select a year.";
    if (!form.km || Number(form.km) <= 0) e.km = "Enter valid KM driven.";
    if (!form.fuel) e.fuel = "Please select fuel type.";
    if (!form.transmission) e.transmission = "Please select transmission.";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    console.log("Sell Car Form Submission:", form);
    setSubmitted(true);
    toast({ title: "Submission received!", description: "Our team will contact you within 2 hours." });
  };

  if (submitted) {
    return (
      <section id="sell-car-form" className="py-12 sm:py-16 bg-muted">
        <Container>
          <div className="max-w-[600px] mx-auto rounded-2xl bg-card border border-border shadow-md p-8 text-center space-y-4">
            <div className="text-5xl">🎉</div>
            <h3 className="text-2xl font-bold text-foreground">Request Submitted!</h3>
            <p className="text-muted-foreground">Our team will call you within 2 hours on <span className="font-semibold text-foreground">{form.phone}</span>.</p>
            <Button onClick={() => { setSubmitted(false); setForm({ name: "", phone: "", brand: "", model: "", year: "", km: "", fuel: "", transmission: "", expectedPrice: "" }); }} variant="outline" className="mt-2">
              Submit Another Car
            </Button>
          </div>
        </Container>
      </section>
    );
  }

  return (
    <section id="sell-car-form" className="py-12 sm:py-16 bg-muted">
      <Container>
        <div className="max-w-[600px] mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-bold text-logo-blue">Get Free Car Evaluation</h2>
            <p className="text-muted-foreground mt-2 text-sm">Fill in your details and we'll get back to you within 2 hours.</p>
          </div>
          <form
            onSubmit={handleSubmit}
            className="rounded-2xl bg-card border border-border shadow-md p-6 sm:p-8 space-y-5"
          >
            {/* Name + Phone */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label htmlFor="name">Full Name <span className="text-destructive">*</span></Label>
                <Input id="name" placeholder="e.g. Ravi Kumar" value={form.name} onChange={e => set("name", e.target.value)} className={errors.name ? "border-destructive" : ""} />
                {errors.name && <p className="text-xs text-destructive">{errors.name}</p>}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="phone">Phone Number <span className="text-destructive">*</span></Label>
                <Input id="phone" type="tel" placeholder="e.g. 9876543210" maxLength={10} value={form.phone} onChange={e => set("phone", e.target.value.replace(/\D/g, ""))} className={errors.phone ? "border-destructive" : ""} />
                {errors.phone && <p className="text-xs text-destructive">{errors.phone}</p>}
              </div>
            </div>

            {/* Brand + Model */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>Car Brand <span className="text-destructive">*</span></Label>
                <Select value={form.brand} onValueChange={v => set("brand", v)}>
                  <SelectTrigger className={errors.brand ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select brand" />
                  </SelectTrigger>
                  <SelectContent>
                    {BRANDS.map(b => <SelectItem key={b} value={b}>{b}</SelectItem>)}
                  </SelectContent>
                </Select>
                {errors.brand && <p className="text-xs text-destructive">{errors.brand}</p>}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="model">Car Model <span className="text-destructive">*</span></Label>
                <Input id="model" placeholder="e.g. i20 Sportz" value={form.model} onChange={e => set("model", e.target.value)} className={errors.model ? "border-destructive" : ""} />
                {errors.model && <p className="text-xs text-destructive">{errors.model}</p>}
              </div>
            </div>

            {/* Year + KM */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>Model Year <span className="text-destructive">*</span></Label>
                <Select value={form.year} onValueChange={v => set("year", v)}>
                  <SelectTrigger className={errors.year ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select year" />
                  </SelectTrigger>
                  <SelectContent>
                    {YEARS.map(y => <SelectItem key={y} value={y}>{y}</SelectItem>)}
                  </SelectContent>
                </Select>
                {errors.year && <p className="text-xs text-destructive">{errors.year}</p>}
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="km">KM Driven <span className="text-destructive">*</span></Label>
                <Input id="km" type="number" placeholder="e.g. 35000" min={0} value={form.km} onChange={e => set("km", e.target.value)} className={errors.km ? "border-destructive" : ""} />
                {errors.km && <p className="text-xs text-destructive">{errors.km}</p>}
              </div>
            </div>

            {/* Fuel + Transmission */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>Fuel Type <span className="text-destructive">*</span></Label>
                <Select value={form.fuel} onValueChange={v => set("fuel", v)}>
                  <SelectTrigger className={errors.fuel ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select fuel" />
                  </SelectTrigger>
                  <SelectContent>
                    {FUEL_TYPES.map(f => <SelectItem key={f} value={f}>{f}</SelectItem>)}
                  </SelectContent>
                </Select>
                {errors.fuel && <p className="text-xs text-destructive">{errors.fuel}</p>}
              </div>
              <div className="space-y-1.5">
                <Label>Transmission <span className="text-destructive">*</span></Label>
                <Select value={form.transmission} onValueChange={v => set("transmission", v)}>
                  <SelectTrigger className={errors.transmission ? "border-destructive" : ""}>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {TRANSMISSIONS.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
                {errors.transmission && <p className="text-xs text-destructive">{errors.transmission}</p>}
              </div>
            </div>

            {/* Expected Price */}
            <div className="space-y-1.5">
              <Label htmlFor="expectedPrice">Expected Price <span className="text-muted-foreground text-xs">(Optional)</span></Label>
              <Input id="expectedPrice" placeholder="e.g. ₹4,50,000" value={form.expectedPrice} onChange={e => set("expectedPrice", e.target.value)} />
            </div>

            {/* Photo Upload */}
            <div className="space-y-1.5">
              <Label>Upload Car Photos <span className="text-muted-foreground text-xs">(Optional)</span></Label>
              <label className="flex flex-col items-center justify-center w-full h-28 rounded-xl border-2 border-dashed border-border bg-muted/50 cursor-pointer hover:bg-muted transition-colors">
                <Upload className="w-6 h-6 text-muted-foreground mb-1" />
                <span className="text-sm text-muted-foreground">Click to upload photos</span>
                <span className="text-xs text-muted-foreground mt-0.5">JPG, PNG up to 10MB each</span>
                <input type="file" accept="image/*" multiple className="hidden" />
              </label>
            </div>

            <Button type="submit" className="w-full h-12 bg-primary hover:bg-primary-dark text-white font-bold text-base rounded-xl">
              Get Free Evaluation
            </Button>

            <p className="text-center text-xs text-muted-foreground">
              By submitting you agree to be contacted by our team via phone or WhatsApp.
            </p>
          </form>
        </div>
      </Container>
    </section>
  );
};

export default SellCarForm;
