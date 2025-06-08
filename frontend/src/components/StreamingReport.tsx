import React, { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StreamingReportProps {
  content: string;
  isStreaming: boolean;
  className?: string;
}

export const StreamingReport: React.FC<StreamingReportProps> = ({
  content,
  isStreaming,
  className,
}) => {
  const endRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new content is added
  useEffect(() => {
    if (isStreaming && endRef.current) {
      // Use requestAnimationFrame for smoother scrolling
      requestAnimationFrame(() => {
        endRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "end",
          inline: "nearest",
        });
      });
    }
  }, [content, isStreaming]);

  if (!content && !isStreaming) {
    return null;
  }

  return (
    <Card
      ref={containerRef}
      className={cn("bg-neutral-900 border-neutral-700", className)}
    >
      <CardContent className="p-4">
        {isStreaming && (
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-blue-300">
              Generating report...
            </span>
          </div>
        )}

        <div className="prose prose-sm max-w-none prose-invert max-h-[60vh] overflow-y-auto pr-4 scrollbar-custom text-white">
          <ReactMarkdown>{content}</ReactMarkdown>
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1" />
          )}
        </div>

        <div ref={endRef} />
      </CardContent>
    </Card>
  );
};
