import { Link } from "react-router-dom";
import { BUSINESS_NAME, EMBLEM_PATH } from "@/config/business";

interface LogoProps {
  className?: string;
  linkToHome?: boolean;
  textClassName?: string;
}

const Logo = ({ className = "h-10", linkToHome = true, textClassName = "" }: LogoProps) => {
  const content = (
    <span className="inline-flex items-center gap-2 shrink-0">
      {EMBLEM_PATH && (
        <img
          src={EMBLEM_PATH}
          alt=""
          aria-hidden
          className={`w-auto object-contain shrink-0 rounded-full ${className}`}
        />
      )}
      <span className={`font-bold text-lg tracking-tight whitespace-nowrap ${textClassName}`}>
        {BUSINESS_NAME}
      </span>
    </span>
  );

  if (linkToHome) {
    return (
      <Link to="/" className={`inline-flex items-center ${textClassName}`}>
        {content}
      </Link>
    );
  }
  return content;
};

export default Logo;
