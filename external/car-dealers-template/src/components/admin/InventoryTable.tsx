import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import CarRow from "./CarRow";
import type { AdminCar } from "@/data/admin-cars";

interface InventoryTableProps {
  cars: AdminCar[];
  onEdit: (car: AdminCar) => void;
  onDelete: (car: AdminCar) => void;
  onMarkSold: (car: AdminCar) => void;
}

const InventoryTable = ({
  cars,
  onEdit,
  onDelete,
  onMarkSold,
}: InventoryTableProps) => {
  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-card shadow-sm">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-20">Image</TableHead>
            <TableHead>Car Name</TableHead>
            <TableHead>Year</TableHead>
            <TableHead>KM Driven</TableHead>
            <TableHead>Fuel</TableHead>
            <TableHead>Price</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-36 text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {cars.length === 0 ? (
            <TableRow>
              <TableCell
                colSpan={8}
                className="h-32 text-center text-muted-foreground"
              >
                No cars in inventory. Add a new car to get started.
              </TableCell>
            </TableRow>
          ) : (
            cars.map((car) => (
              <CarRow
                key={car.id}
                car={car}
                onEdit={onEdit}
                onDelete={onDelete}
                onMarkSold={onMarkSold}
              />
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
};

export default InventoryTable;
