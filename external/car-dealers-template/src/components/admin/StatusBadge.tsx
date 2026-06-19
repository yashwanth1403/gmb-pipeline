import { cn } from "@/lib/utils";
import type { CarStatus } from "@/data/admin-cars";

interface StatusBadgeProps {
  status: CarStatus;
  className?: string;
}

const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  const isAvailable = status === "Available";

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold",
        isAvailable
          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400"
          : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
        className
      )}
    >
      {status}
    </span>
  );
};

export default StatusBadge;
