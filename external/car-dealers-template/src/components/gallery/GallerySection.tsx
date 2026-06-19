import Container from "@/components/Container";
import { GALLERY_IMAGES } from "@/config/business";

function gridClass(count: number): string {
  if (count === 1) return "grid-cols-1 max-w-lg mx-auto";
  if (count === 2) return "grid-cols-2 max-w-2xl mx-auto";
  if (count === 3) return "grid-cols-3";
  if (count === 4) return "grid-cols-2 sm:grid-cols-2";
  return "grid-cols-2 sm:grid-cols-3";
}

const GallerySection = () => {
  if (!GALLERY_IMAGES.length) return null;

  const count = GALLERY_IMAGES.length;

  return (
    <section className="py-12 sm:py-16">
      <Container className="space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold sm:text-3xl text-logo-blue">Our Gallery</h2>
          <p className="text-muted-foreground">A look inside our showroom &amp; happy customers</p>
        </div>

        <div className={`grid gap-4 sm:gap-6 ${gridClass(count)}`}>
          {GALLERY_IMAGES.map((img, i) => (
            <div
              key={i}
              className="aspect-[4/3] rounded-xl overflow-hidden shadow-md hover:shadow-lg transition-shadow bg-muted"
            >
              <img
                src={img.src}
                alt={img.alt}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
};

export default GallerySection;
