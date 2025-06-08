import React from "react";
import {
  CheckCircle,
  Clock,
  Search,
  BarChart3,
  FileText,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import ReactMarkdown from "react-markdown";

export interface ResearchStage {
  id: string;
  title: string;
  description?: string;
  status: "pending" | "active" | "completed" | "error";
  icon: "search" | "analysis" | "report" | "thinking";
  output?: string;
  startTime?: Date;
  endTime?: Date;
  progress?: number; // Progress percentage (0-100)
}

interface ResearchStagePanelProps {
  stages: ResearchStage[];
  currentStage?: string;
  className?: string;
}

const getStageIcon = (
  icon: ResearchStage["icon"],
  status: ResearchStage["status"]
) => {
  const iconClass = cn(
    "w-5 h-5",
    status === "completed"
      ? "text-green-500"
      : status === "active"
      ? "text-blue-500"
      : status === "error"
      ? "text-red-500"
      : "text-gray-400"
  );

  switch (icon) {
    case "search":
      return <Search className={iconClass} />;
    case "analysis":
      return <BarChart3 className={iconClass} />;
    case "report":
      return <FileText className={iconClass} />;
    case "thinking":
    default:
      return <Clock className={iconClass} />;
  }
};

const getStatusIcon = (status: ResearchStage["status"]) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    case "active":
      return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
    case "error":
      return <div className="w-4 h-4 rounded-full bg-red-500" />;
    default:
      return <div className="w-4 h-4 rounded-full bg-gray-300" />;
  }
};

const StageItem: React.FC<{ stage: ResearchStage; isActive: boolean }> = ({
  stage,
  isActive,
}) => {
  const duration =
    stage.startTime && stage.endTime
      ? Math.round((stage.endTime.getTime() - stage.startTime.getTime()) / 1000)
      : null;

  return (
    <div
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg transition-all duration-200",
        isActive
          ? "bg-neutral-800 border-l-4 border-blue-500"
          : "hover:bg-neutral-800/50"
      )}
    >
      <div className="flex flex-col items-center gap-2 mt-1">
        {getStageIcon(stage.icon, stage.status)}
        {getStatusIcon(stage.status)}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between">
          <h3
            className={cn(
              "font-medium text-sm",
              isActive ? "text-blue-300" : "text-neutral-100"
            )}
          >
            {stage.title}
          </h3>
          {duration && (
            <span className="text-xs text-neutral-500">{duration}s</span>
          )}
        </div>

        {stage.description && (
          <p className="text-xs text-neutral-400 mt-1">{stage.description}</p>
        )}

        {/* Progress bar for all stages except pending */}
        {stage.status !== "pending" && (
          <div className="mt-2">
            <div className="w-full bg-neutral-700 rounded-full h-1">
              <div
                className={cn(
                  "h-1 rounded-full transition-all duration-300",
                  stage.status === "completed"
                    ? "bg-green-500"
                    : stage.status === "active"
                    ? "bg-blue-500 animate-pulse"
                    : stage.status === "error"
                    ? "bg-red-500"
                    : "bg-neutral-500"
                )}
                style={{
                  width: `${
                    stage.status === "completed"
                      ? 100
                      : stage.progress || (stage.status === "active" ? 50 : 0)
                  }%`,
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const StageOutput: React.FC<{ stage: ResearchStage }> = ({ stage }) => {
  if (!stage.output) return null;

  return (
    <Card className="mt-4 bg-neutral-800 border-neutral-700">
      <CardContent className="p-4">
        <div className="flex items-center gap-2 mb-3">
          {getStageIcon(stage.icon, stage.status)}
          <h4 className="font-medium text-sm text-neutral-100">
            {stage.title}
          </h4>
        </div>
        <div className="prose prose-sm max-w-none prose-invert">
          <ReactMarkdown>{stage.output}</ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  );
};

export const ResearchStagePanel: React.FC<ResearchStagePanelProps> = ({
  stages,
  currentStage,
  className,
}) => {
  const activeStage = stages.find((stage) => stage.id === currentStage);
  const completedStages = stages.filter(
    (stage) => stage.status === "completed"
  );

  return (
    <div className={cn("space-y-4", className)}>
      {/* Stages Timeline */}
      <div className="space-y-2">
        {stages.map((stage) => (
          <StageItem
            key={stage.id}
            stage={stage}
            isActive={stage.id === currentStage}
          />
        ))}
      </div>

      {/* Active Stage Output */}
      {/* {activeStage && activeStage.output && <StageOutput stage={activeStage} />} */}

      {/* Completed Stages Output (collapsed) */}
      {/* {completedStages.length > 0 && (
        <div className="space-y-2">
          {completedStages.map((stage) => (
            <StageOutput key={`output-${stage.id}`} stage={stage} />
          ))}
        </div>
      )} */}
    </div>
  );
};
