import React from "react";

interface CarDescriptionProps {
  description: string;
}

export const CarDescription = ({ description }: CarDescriptionProps) => {
  return (
    <div className="bg-card rounded-xl border border-border p-5 sm:p-6 shadow-sm">
      <h2 className="text-xl font-bold text-logo-blue mb-4 flex items-center gap-2">
        <span className="w-1.5 h-6 bg-primary rounded-full inline-block"></span>
        Seller Notes
      </h2>
      <div className="bg-muted/40 rounded-lg p-4 border border-border">
        <p className="text-sm sm:text-base leading-relaxed text-foreground whitespace-pre-line font-medium">
          {description}
        </p>
      </div>
    </div>
  );
};
