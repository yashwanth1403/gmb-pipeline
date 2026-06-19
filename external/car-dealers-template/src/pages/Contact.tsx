import SiteLayout from "@/components/SiteLayout";
import Container from "@/components/Container";
import { ContactHeader } from "@/components/contact/ContactHeader";
import { ContactCards } from "@/components/contact/ContactCards";
import { ContactForm } from "@/components/contact/ContactForm";
import { ShowroomMap } from "@/components/contact/ShowroomMap";
import { ContactCTA } from "@/components/contact/ContactCTA";

const Contact = () => {
  return (
    <SiteLayout>
      {/* Dark hero header — full-bleed, handles its own bg */}
      <ContactHeader />

      <div className="pb-20 pt-4">
        <Container>
          <ContactCards />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14">
            <ContactForm />
            <ShowroomMap />
          </div>

          <ContactCTA />
        </Container>
      </div>
    </SiteLayout>
  );
};

export default Contact;
