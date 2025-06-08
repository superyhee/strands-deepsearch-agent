import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Loader2,
  Activity,
  Info,
  Search,
  TextSearch,
  Brain,
  Pen,
  ChevronDown,
  ChevronUp,
  CheckCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Progress } from "@/components/ui/progress";

export interface ProcessedEvent {
  title: string;
  data: any;
  progress?: number;
  status?: "pending" | "processing" | "completed";
  step?: string;
  stage?: string;
}

interface ActivityTimelineProps {
  processedEvents: ProcessedEvent[];
  isLoading: boolean;
}

export function ActivityTimeline({
  processedEvents,
  isLoading,
}: ActivityTimelineProps) {
  const [isTimelineCollapsed, setIsTimelineCollapsed] =
    useState<boolean>(false);
  const [overallProgress, setOverallProgress] = useState(0);

  const getEventIcon = (title: string, index: number, status?: string) => {
    if (status === "completed") {
      return <CheckCircle className="h-4 w-4 text-green-400" />;
    }
    if (index === 0 && isLoading && processedEvents.length === 0) {
      return <Loader2 className="h-4 w-4 text-neutral-400 animate-spin" />;
    }
    if (title.toLowerCase().includes("generating")) {
      return <TextSearch className="h-4 w-4 text-neutral-400" />;
    } else if (title.toLowerCase().includes("thinking")) {
      return <Loader2 className="h-4 w-4 text-neutral-400 animate-spin" />;
    } else if (title.toLowerCase().includes("reflection")) {
      return <Brain className="h-4 w-4 text-neutral-400" />;
    } else if (title.toLowerCase().includes("research")) {
      return <Search className="h-4 w-4 text-neutral-400" />;
    } else if (title.toLowerCase().includes("finalizing")) {
      return <Pen className="h-4 w-4 text-neutral-400" />;
    }
    return <Activity className="h-4 w-4 text-neutral-400" />;
  };

  useEffect(() => {
    if (!isLoading && processedEvents.length !== 0) {
      setIsTimelineCollapsed(true);
    }
  }, [isLoading, processedEvents]);

  useEffect(() => {
    if (processedEvents.length > 0) {
      const completedEvents = processedEvents.filter(
        (event) => event.status === "completed"
      ).length;
      const progress = (completedEvents / processedEvents.length) * 100;
      setOverallProgress(progress);
    } else {
      setOverallProgress(0);
    }
  }, [processedEvents]);

  return (
    <Card className="border-none rounded-lg bg-neutral-700 max-h-96">
      <CardHeader>
        <CardDescription className="flex items-center justify-between">
          <div
            className="flex items-center justify-start text-sm w-full cursor-pointer gap-2 text-neutral-100"
            onClick={() => setIsTimelineCollapsed(!isTimelineCollapsed)}
          >
            <div className="flex-1">
              Research Progress
              {isTimelineCollapsed ? (
                <ChevronDown className="h-4 w-4 inline-block ml-2" />
              ) : (
                <ChevronUp className="h-4 w-4 inline-block ml-2" />
              )}
            </div>
            <div className="flex items-center gap-2">
              <Progress value={overallProgress} className="w-24" />
              <span className="text-xs">{Math.round(overallProgress)}%</span>
            </div>
          </div>
        </CardDescription>
      </CardHeader>
      {!isTimelineCollapsed && (
        <ScrollArea className="max-h-96 overflow-y-auto">
          <CardContent>
            {isLoading && processedEvents.length === 0 && (
              <div className="relative pl-8 pb-4">
                <div className="absolute left-3 top-3.5 h-full w-0.5 bg-neutral-800" />
                <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-neutral-800 flex items-center justify-center ring-4 ring-neutral-900">
                  <Loader2 className="h-3 w-3 text-neutral-400 animate-spin" />
                </div>
                <div>
                  <p className="text-sm text-neutral-300 font-medium">
                    Initializing search...
                  </p>
                </div>
              </div>
            )}
            {processedEvents.length > 0 ? (
              <div className="space-y-0">
                {processedEvents.map((eventItem, index) => (
                  <div
                    key={index}
                    className={`relative pl-8 pb-4 transition-all duration-300 ${
                      eventItem.status === "processing" ? "scale-105" : ""
                    }`}
                  >
                    {index < processedEvents.length - 1 ||
                    (isLoading && index === processedEvents.length - 1) ? (
                      <div className="absolute left-3 top-3.5 h-full w-0.5 bg-neutral-600" />
                    ) : null}
                    <div
                      className={`absolute left-0.5 top-2 h-6 w-6 rounded-full flex items-center justify-center ring-4 transition-colors duration-300 ${
                        eventItem.status === "completed"
                          ? "bg-green-600 ring-neutral-700"
                          : eventItem.status === "processing"
                          ? "bg-blue-600 ring-neutral-700"
                          : "bg-neutral-600 ring-neutral-700"
                      }`}
                    >
                      {getEventIcon(eventItem.title, index, eventItem.status)}
                    </div>
                    <div>
                      <p className="text-sm text-neutral-200 font-medium mb-0.5 flex items-center justify-between">
                        <span>{eventItem.title}</span>
                        {eventItem.progress !== undefined && (
                          <span className="text-xs text-neutral-400">
                            {eventItem.progress}%
                          </span>
                        )}
                      </p>
                      <p className="text-xs text-neutral-300 leading-relaxed">
                        {typeof eventItem.data === "string"
                          ? eventItem.data
                          : Array.isArray(eventItem.data)
                          ? (eventItem.data as string[]).join(", ")
                          : JSON.stringify(eventItem.data)}
                      </p>
                      {eventItem.progress !== undefined && (
                        <Progress
                          value={eventItem.progress}
                          className="w-full mt-2 h-1"
                        />
                      )}
                    </div>
                  </div>
                ))}
                {isLoading && processedEvents.length > 0 && (
                  <div className="relative pl-8 pb-4">
                    <div className="absolute left-0.5 top-2 h-5 w-5 rounded-full bg-neutral-600 flex items-center justify-center ring-4 ring-neutral-700">
                      <Loader2 className="h-3 w-3 text-neutral-400 animate-spin" />
                    </div>
                    <div>
                      <p className="text-sm text-neutral-300 font-medium">
                        Processing...
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : !isLoading ? (
              <div className="flex flex-col items-center justify-center h-full text-neutral-500 pt-10">
                <Info className="h-6 w-6 mb-3" />
                <p className="text-sm">No activity to display.</p>
                <p className="text-xs text-neutral-600 mt-1">
                  Timeline will update during processing.
                </p>
              </div>
            ) : null}
          </CardContent>
        </ScrollArea>
      )}
    </Card>
  );
}
