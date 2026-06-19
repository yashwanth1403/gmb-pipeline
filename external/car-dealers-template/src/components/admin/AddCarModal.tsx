import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { BRANDS } from "@/data/cars";
import type { AdminCar } from "@/data/admin-cars";

const FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Electric"] as const;
const TRANSMISSIONS = ["Manual", "Automatic"] as const;

export type AdminCarFormData = Omit<AdminCar, "id" | "status" | "images"> & {
  emi?: number;
};

interface AddCarModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialCar?: AdminCar | null;
  onSubmit: (data: AdminCarFormData, id?: string) => void;
}

const getDefaultFormData = (): AdminCarFormData => ({
  name: "",
  brand: "Maruti",
  year: new Date().getFullYear(),
  km: 0,
  fuel: "Petrol",
  transmission: "Manual",
  price: 0,
  emi: undefined,
  description: "",
  image: "",
});

const AddCarModal = ({
  open,
  onOpenChange,
  initialCar,
  onSubmit,
}: AddCarModalProps) => {
  const isEditing = !!initialCar;
  const [formData, setFormData] = useState<AdminCarFormData>(getDefaultFormData);

  useEffect(() => {
    if (open) {
      if (initialCar) {
        setFormData({
          name: initialCar.name,
          brand: initialCar.brand,
          year: initialCar.year,
          km: initialCar.km,
          fuel: initialCar.fuel,
          transmission: initialCar.transmission,
          price: initialCar.price,
          emi: initialCar.emi,
          description: initialCar.description ?? "",
          image: initialCar.image,
        });
      } else {
        setFormData(getDefaultFormData());
      }
    }
  }, [open, initialCar]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData, initialCar?.id);
    onOpenChange(false);
  };

  const brandsForSelect = BRANDS.filter((b) => b !== "All");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto rounded-xl sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit Car" : "Add New Car"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="name">Car Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
              placeholder="e.g. Honda City VX CVT"
              required
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="brand">Brand</Label>
            <Select
              value={formData.brand}
              onValueChange={(v) => setFormData((p) => ({ ...p, brand: v }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select brand" />
              </SelectTrigger>
              <SelectContent>
                {brandsForSelect.map((b) => (
                  <SelectItem key={b} value={b}>
                    {b}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="year">Model Year</Label>
              <Input
                id="year"
                type="number"
                min={1990}
                max={new Date().getFullYear() + 1}
                value={formData.year || ""}
                onChange={(e) =>
                  setFormData((p) => ({ ...p, year: parseInt(e.target.value, 10) || 0 }))
                }
                placeholder="2023"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="km">KM Driven</Label>
              <Input
                id="km"
                type="number"
                min={0}
                value={formData.km || ""}
                onChange={(e) =>
                  setFormData((p) => ({ ...p, km: parseInt(e.target.value, 10) || 0 }))
                }
                placeholder="0"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="fuel">Fuel Type</Label>
              <select
                id="fuel"
                value={formData.fuel}
                onChange={(e) =>
                  setFormData((p) => ({
                    ...p,
                    fuel: e.target.value as AdminCar["fuel"],
                  }))
                }
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {FUEL_TYPES.map((f) => (
                  <option key={f} value={f}>
                    {f}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="transmission">Transmission</Label>
              <select
                id="transmission"
                value={formData.transmission}
                onChange={(e) =>
                  setFormData((p) => ({
                    ...p,
                    transmission: e.target.value as AdminCar["transmission"],
                  }))
                }
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {TRANSMISSIONS.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="price">Price (₹)</Label>
              <Input
                id="price"
                type="number"
                min={0}
                value={formData.price || ""}
                onChange={(e) =>
                  setFormData((p) => ({
                    ...p,
                    price: parseInt(e.target.value, 10) || 0,
                  }))
                }
                placeholder="1000000"
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="emi">EMI (optional, ₹/mo)</Label>
              <Input
                id="emi"
                type="number"
                min={0}
                value={formData.emi ?? ""}
                onChange={(e) => {
                  const v = e.target.value;
                  const n = parseInt(v, 10);
                  setFormData((p) => ({ ...p, emi: v === "" || isNaN(n) ? undefined : n }));
                }}
                placeholder="Optional"
              />
            </div>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description ?? ""}
              onChange={(e) =>
                setFormData((p) => ({ ...p, description: e.target.value }))
              }
              placeholder="Brief description of the car..."
              rows={3}
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="image">Image URL</Label>
            <Input
              id="image"
              value={formData.image}
              onChange={(e) => setFormData((p) => ({ ...p, image: e.target.value }))}
              placeholder="/images/car.jpg"
            />
          </div>

          <div className="grid gap-2">
            <Label>Upload Images</Label>
            <div className="flex h-24 items-center justify-center rounded-xl border-2 border-dashed border-muted-foreground/25 bg-muted/50 text-sm text-muted-foreground">
              Placeholder — Upload will be available with backend
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" className="rounded-xl">
              Save Car
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddCarModal;
