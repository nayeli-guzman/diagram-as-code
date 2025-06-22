import React from "react";
import { Heart } from "lucide-react";

interface TeamBrandingProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  showIcon?: boolean;
}

const TeamBranding: React.FC<TeamBrandingProps> = ({
  size = "md",
  className = "",
  showIcon = true,
}) => {
  const sizeClasses = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  };

  const iconSizes = {
    sm: 12,
    md: 14,
    lg: 16,
  };

  return (
    <div
      className={`flex items-center space-x-1 text-gray-600 ${sizeClasses[size]} ${className}`}
    >
      {showIcon && (
        <Heart size={iconSizes[size]} className="text-blue-600 fill-current" />
      )}
      <span>
        Creado por{" "}
        <span className="font-semibold text-blue-600">
          "Todo va a estar Bien"
        </span>
      </span>
    </div>
  );
};

export default TeamBranding;
