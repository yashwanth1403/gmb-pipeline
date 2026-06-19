import React from "react";
import { Clock, MapPin } from "lucide-react";
import { BUSINESS_NAME, CONTACT, HOURS } from "@/config/business";

export const ShowroomMap = () => {
  return (
    <div
      className="bg-card border border-border rounded-xl shadow-sm overflow-hidden"
      id="location"
    >
      <div className="p-6 md:p-8">
        <h2 className="text-2xl font-bold text-logo-blue mb-6 flex items-center gap-2">
          <span className="w-1.5 h-6 bg-primary rounded-full inline-block"></span>
          Visit Our Showroom
        </h2>

        {/* Map Embed Placeholder */}
        <div className="w-full h-[300px] sm:h-[400px] bg-muted rounded-xl mb-6 relative overflow-hidden group">
          {/* Using a placeholder static map image or an iframe */}
          <iframe
            src={CONTACT.mapsEmbedUrl}
            width="100%"
            height="100%"
            style={{ border: 0 }}
            allowFullScreen={false}
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
            title={`${BUSINESS_NAME} Location`}
            className="filter grayscale-[0.2] contrast-[0.9] opacity-90 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-500"
          ></iframe>
        </div>

        {/* Address and Hours */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-muted/40 rounded-xl p-5 border border-border">
          {/* Address */}
          <div className="flex items-start gap-4">
            <div className="bg-background w-10 h-10 rounded-full flex items-center justify-center shrink-0 border border-border shadow-sm">
              <MapPin size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="font-bold text-foreground mb-1">
                Showroom Address
              </h3>
              <p className="text-muted-foreground text-sm font-medium leading-relaxed">
                {CONTACT.address}
              </p>
            </div>
          </div>

          {/* Opening Hours */}
          <div className="flex items-start gap-4">
            <div className="bg-background w-10 h-10 rounded-full flex items-center justify-center shrink-0 border border-border shadow-sm">
              <Clock size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="font-bold text-foreground mb-1">Opening Hours</h3>
              <p className="text-muted-foreground text-sm font-medium leading-relaxed">
                {HOURS.map((h, i) => (
                  <React.Fragment key={h.days}>
                    <span className="text-foreground">{h.days}:</span> {h.hours}
                    {i < HOURS.length - 1 && <br />}
                  </React.Fragment>
                ))}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
