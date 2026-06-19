/** ── helpers ── */
interface PlaceholderProps {
  label: string;
}

export const Placeholder = ({ label }: PlaceholderProps) => (
  <div className="rounded-lg border-2 border-dashed border-border bg-card p-8 text-center">
    <p className="text-sm font-medium text-muted-foreground">{label}</p>
  </div>
);
