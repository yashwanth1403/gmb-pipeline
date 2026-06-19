import { useState } from "react";
import Container from "@/components/Container";
import AdminHeader from "@/components/admin/AdminHeader";
import InventoryTable from "@/components/admin/InventoryTable";
import AddCarModal, { type AdminCarFormData } from "@/components/admin/AddCarModal";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  type AdminCar,
  INITIAL_ADMIN_CARS,
} from "@/data/admin-cars";

/**
 * /admin — Car Inventory Dashboard
 * Allows dealer to add, edit, delete, and mark cars as sold.
 * No authentication in Phase 1.
 */
const Admin = () => {
  const [cars, setCars] = useState<AdminCar[]>(() => [...INITIAL_ADMIN_CARS]);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCar, setEditingCar] = useState<AdminCar | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AdminCar | null>(null);

  const handleAddCar = () => {
    setEditingCar(null);
    setModalOpen(true);
  };

  const handleEdit = (car: AdminCar) => {
    setEditingCar(car);
    setModalOpen(true);
  };

  const handleModalSubmit = (data: AdminCarFormData, id?: string) => {
    if (id) {
      setCars((prev) =>
        prev.map((c) =>
          c.id === id
            ? {
                ...c,
                ...data,
                emi: data.emi,
                status: c.status,
              }
            : c
        )
      );
    } else {
      const newCar: AdminCar = {
        ...data,
        id: String(Date.now()),
        emi: data.emi,
        status: "Available",
        image: data.image || "",
      };
      setCars((prev) => [...prev, newCar]);
    }
    setModalOpen(false);
    setEditingCar(null);
  };

  const handleDelete = (car: AdminCar) => {
    setDeleteTarget(car);
  };

  const confirmDelete = () => {
    if (deleteTarget) {
      setCars((prev) => prev.filter((c) => c.id !== deleteTarget.id));
      setDeleteTarget(null);
    }
  };

  const handleMarkSold = (car: AdminCar) => {
    setCars((prev) =>
      prev.map((c) =>
        c.id === car.id ? { ...c, status: "Sold" as const } : c
      )
    );
  };

  return (
    <div className="min-h-screen bg-muted">
      <Container className="py-8 space-y-6">
        <AdminHeader onAddCar={handleAddCar} />

        <InventoryTable
          cars={cars}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onMarkSold={handleMarkSold}
        />
      </Container>

      <AddCarModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        initialCar={editingCar}
        onSubmit={handleModalSubmit}
      />

      <AlertDialog open={!!deleteTarget} onOpenChange={() => setDeleteTarget(null)}>
        <AlertDialogContent className="rounded-xl">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete car listing?</AlertDialogTitle>
            <AlertDialogDescription>
              {deleteTarget
                ? `This will permanently remove "${deleteTarget.name}" from inventory. This action cannot be undone.`
                : ""}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Admin;
