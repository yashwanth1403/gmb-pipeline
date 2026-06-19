import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AdminHeaderProps {
  onAddCar: () => void;
}

const AdminHeader = ({ onAddCar }: AdminHeaderProps) => {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
        Car Inventory Dashboard
      </h1>
      <Button
        onClick={onAddCar}
        className="rounded-xl bg-primary text-primary-foreground hover:bg-primary/90"
      >
        <Plus className="h-4 w-4" />
        Add New Car
      </Button>
    </div>
  );
};

export default AdminHeader;
