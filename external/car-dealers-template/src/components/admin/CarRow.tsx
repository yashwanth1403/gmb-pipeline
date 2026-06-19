import { Pencil, Trash2, CheckCircle } from "lucide-react";
import {
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import StatusBadge from "./StatusBadge";
import { formatPrice, formatKm } from "@/data/cars";
import type { AdminCar } from "@/data/admin-cars";

interface CarRowProps {
  car: AdminCar;
  onEdit: (car: AdminCar) => void;
  onDelete: (car: AdminCar) => void;
  onMarkSold: (car: AdminCar) => void;
}

const CarRow = ({ car, onEdit, onDelete, onMarkSold }: CarRowProps) => {
  const isSold = car.status === "Sold";

  return (
    <TableRow>
      <TableCell>
        <div className="h-12 w-16 shrink-0 overflow-hidden rounded-lg bg-muted">
          {car.image ? (
            <img
              src={car.image}
              alt={car.name}
              className="h-full w-full object-cover"
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center text-muted-foreground">
              <span className="text-xs">No image</span>
            </div>
          )}
        </div>
      </TableCell>
      <TableCell className="font-medium">{car.name}</TableCell>
      <TableCell>{car.year}</TableCell>
      <TableCell>{formatKm(car.km)}</TableCell>
      <TableCell>{car.fuel}</TableCell>
      <TableCell className="font-semibold">{formatPrice(car.price)}</TableCell>
      <TableCell>
        <StatusBadge status={car.status} />
      </TableCell>
      <TableCell>
        <TooltipProvider>
          <div className="flex items-center gap-1">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 rounded-lg"
                  onClick={() => onEdit(car)}
                >
                  <Pencil className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Edit</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-9 w-9 rounded-lg text-destructive hover:bg-destructive/10 hover:text-destructive"
                  onClick={() => onDelete(car)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Delete</TooltipContent>
            </Tooltip>
            {!isSold && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-9 w-9 rounded-lg text-emerald-600 hover:bg-blue-500/10 hover:text-emerald-700"
                    onClick={() => onMarkSold(car)}
                  >
                    <CheckCircle className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Mark as Sold</TooltipContent>
              </Tooltip>
            )}
          </div>
        </TooltipProvider>
      </TableCell>
    </TableRow>
  );
};

export default CarRow;
