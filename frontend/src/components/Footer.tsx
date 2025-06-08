import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="py-3 px-6 border-t border-neutral-700 text-center text-neutral-400 text-sm">
      <p>
        © {new Date().getFullYear()} Research Assistant | Powered by AWS Strands
      </p>
    </footer>
  );
};
