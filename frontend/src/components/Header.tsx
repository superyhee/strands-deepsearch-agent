import React from "react";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

interface HeaderProps {
  onNewSearch: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onNewSearch }) => {
  return (
    <header className="py-4 px-6 border-b border-neutral-700 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <Search className="w-5 h-5 text-blue-400" />
        <h1 className="text-xl font-semibold text-neutral-100">
          AWS Research Agent
        </h1>
      </div>
      <Button
        onClick={onNewSearch}
        variant="outline"
        className="bg-neutral-700 border-neutral-600 text-neutral-300 cursor-pointer rounded-xl rounded-t-sm pl-2 "
      >
        New Search
      </Button>
    </header>
  );
};
