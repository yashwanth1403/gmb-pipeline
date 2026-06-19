// All dealer-specific config lives in dealer.json.
// The pipeline writes that file from GBP lead data + LLM — no TypeScript editing needed.
import dealer from "./dealer.json";

export const BUSINESS_NAME    = dealer.name;
export const BUSINESS_CITY    = dealer.city;
export const LOGO_PATH        = dealer.logoPath;
export const EMBLEM_PATH      = dealer.emblemPath;
export const CONTACT          = dealer.contact;
export const HOURS            = dealer.hours;
export const HERO             = dealer.hero;
export const STORY            = dealer.story;
export const STATS            = dealer.stats;
export const RATING           = dealer.rating;
export const FEATURED_CAR_IDS = dealer.featuredCarIds;
export const GALLERY_IMAGES   = dealer.galleryImages;
