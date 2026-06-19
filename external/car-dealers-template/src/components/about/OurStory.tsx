import { STORY, STATS } from "@/config/business";
import Container from "@/components/Container";

const STAT_ACCENTS = [
  "from-logo-blue to-primary",
  "from-blue-500 to-blue-600",
  "from-blue-400 to-blue-500",
  "from-blue-700 to-blue-800",
];

const OurStory = () => (
  <section className="py-16 sm:py-24 bg-white">
    <Container>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center">
        {/* Story text */}
        <div className="space-y-6">
          <div className="space-y-3">
            <span className="inline-block rounded-full bg-primary/15 px-4 py-1.5 text-xs font-semibold uppercase tracking-widest text-logo-blue-light">
              Our Story
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-logo-blue leading-tight">
              {STORY.headline}
            </h2>
          </div>
          {STORY.paragraphs.map((p, i) => (
            <p key={i} className="text-slate-600 leading-relaxed text-base">{p}</p>
          ))}
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-4">
          {STATS.map((s, i) => (
            <div
              key={s.label}
              className="relative rounded-2xl overflow-hidden p-6 flex flex-col gap-1 text-white"
              style={{ background: `linear-gradient(135deg, var(--tw-gradient-stops))` }}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${STAT_ACCENTS[i % STAT_ACCENTS.length]} opacity-100 -z-0`} />
              <div className="relative z-10 flex flex-col gap-1">
                <p className="text-4xl font-black leading-none">{s.metric}</p>
                <p className="font-bold text-sm leading-snug opacity-90">{s.label}</p>
                <p className="text-xs opacity-75 leading-relaxed mt-0.5">{s.desc}</p>
              </div>
              {/* watermark number */}
              <span className="absolute bottom-2 right-3 text-6xl font-black opacity-10 select-none leading-none z-10">
                {String(i + 1)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </Container>
  </section>
);

export default OurStory;
