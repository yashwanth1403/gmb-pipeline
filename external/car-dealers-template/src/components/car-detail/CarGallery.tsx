import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface CarGalleryProps {
  images: string[];
}

export const CarGallery = ({ images }: CarGalleryProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const nextImage = () => setCurrentIndex((prev) => (prev + 1) % images.length);
  const prevImage = () =>
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);

  // Fallback to placeholder images if none provided
  const displayImages =
    images.length > 0
      ? images
      : [
          "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?auto=format&fit=crop&q=80&w=1600",
          "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&q=80&w=1600",
          "https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&q=80&w=1600",
        ];

  return (
    <div className="flex flex-col gap-3">
      {/* Main Image Container */}
      <div className="relative aspect-video sm:aspect-[16/9] w-full bg-muted rounded-xl overflow-hidden group shadow-sm bg-black/5">
        <img
          src={displayImages[currentIndex]}
          alt={`Car view ${currentIndex + 1}`}
          className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
        />

        {/* Navigation Overlays */}
        <div className="absolute inset-0 flex items-center justify-between p-2 sm:p-4 opacity-100 sm:opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={prevImage}
            className="w-10 h-10 rounded-full bg-black/40 text-white flex items-center justify-center hover:bg-black/60 backdrop-blur-md transition-all sm:scale-110 shadow-lg border border-white/20"
            aria-label="Previous image"
          >
            <ChevronLeft size={24} />
          </button>
          <button
            onClick={nextImage}
            className="w-10 h-10 rounded-full bg-black/40 text-white flex items-center justify-center hover:bg-black/60 backdrop-blur-md transition-all sm:scale-110 shadow-lg border border-white/20"
            aria-label="Next image"
          >
            <ChevronRight size={24} />
          </button>
        </div>
      </div>

      {/* Thumbnail Strip */}
      <div className="flex gap-2.5 overflow-x-auto pb-2 scrollbar-none snap-x">
        {displayImages.map((img, idx) => (
          <button
            key={idx}
            onClick={() => setCurrentIndex(idx)}
            className={`relative shrink-0 w-[4.5rem] h-14 sm:w-28 sm:h-20 rounded-lg overflow-hidden border-2 snap-center transition-all ${
              idx === currentIndex
                ? "border-primary scale-100 opacity-100"
                : "border-transparent opacity-70 hover:opacity-100"
            }`}
          >
            <img
              src={img}
              alt={`Thumbnail ${idx + 1}`}
              className="w-full h-full object-cover"
            />
          </button>
        ))}
      </div>
    </div>
  );
};
