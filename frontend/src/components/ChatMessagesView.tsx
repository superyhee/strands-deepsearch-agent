import type React from "react";
import type { Message } from "@langchain/langgraph-sdk";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Loader2,
  Copy,
  CopyCheck,
  CheckCircle,
  Clock,
  Search,
  BarChart3,
  FileText,
} from "lucide-react";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import { useState, ReactNode, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ActivityTimeline,
  ProcessedEvent,
} from "@/components/ActivityTimeline"; // Assuming ActivityTimeline is in the same dir or adjust path
import { StreamingReport } from "@/components/StreamingReport";
import {
  ResearchStagePanel,
  ResearchStage,
} from "@/components/ResearchStagePanel";
import remarkGfm from "remark-gfm";

// Helper function to convert ProcessedEvent to ResearchStage
const convertEventsToStages = (
  events: ProcessedEvent[],
  currentStatus: string,
  currentProgress: number = 0
): ResearchStage[] => {
  const stages: ResearchStage[] = [
    {
      id: "initialization",
      title: "Initialization",
      description: "Preparing research environment",
      status: "pending",
      icon: "thinking",
      progress: 0,
    },
    {
      id: "research",
      title: "Information Collection",
      description: "Searching relevant information and data",
      status: "pending",
      icon: "search",
      progress: 0,
    },
    {
      id: "analysis",
      title: "Analysis",
      description: "Analyzing collected information",
      status: "pending",
      icon: "analysis",
      progress: 0,
    },
    {
      id: "report",
      title: "Generate Report",
      description: "Organizing and generating final report",
      status: "pending",
      icon: "report",
      progress: 0,
    },
  ];

  // Update stages based on events and current progress
  events.forEach((event) => {
    const title = event.title.toLowerCase();
    let stageId = "";

    // Check for stage field first (from backend), then step field, then title
    if (event.data && typeof event.data === "object" && event.data.stage) {
      stageId = event.data.stage;
    } else if (event.step) {
      // Map step to stage
      if (event.step === "initialization") {
        stageId = "initialization";
      } else if (
        event.step.includes("research") ||
        event.step.includes("additional_research")
      ) {
        stageId = "research";
      } else if (event.step.includes("analysis")) {
        stageId = "analysis";
      } else if (
        event.step.includes("report") ||
        event.step === "final_report" ||
        event.step === "report_streaming" ||
        event.step === "report_streaming_start"
      ) {
        stageId = "report";
      }
    } else {
      // Fallback to title-based detection with English keywords
      if (title.includes("initialization") || title.includes("starting")) {
        stageId = "initialization";
      } else if (
        title.includes("collection") ||
        title.includes("collecting") ||
        title.includes("research") ||
        title.includes("search")
      ) {
        stageId = "research";
      } else if (title.includes("analysis") || title.includes("analyzing")) {
        stageId = "analysis";
      } else if (title.includes("report") || title.includes("generating")) {
        stageId = "report";
      }
    }

    if (stageId) {
      const stage = stages.find((s) => s.id === stageId);
      if (stage) {
        stage.status = event.status === "completed" ? "completed" : "active";
        stage.description = event.title;

        // When a stage becomes active, mark previous stages as completed
        if (stage.status === "active") {
          const stageOrder = [
            "initialization",
            "research",
            "analysis",
            "report",
          ];
          const currentIndex = stageOrder.indexOf(stageId);

          // Mark all previous stages as completed
          for (let i = 0; i < currentIndex; i++) {
            const prevStage = stages.find((s) => s.id === stageOrder[i]);
            if (
              prevStage &&
              prevStage.status !== "completed" &&
              prevStage.status !== "error"
            ) {
              prevStage.status = "completed";
              prevStage.progress = 100;
            }
          }
        }

        // Set progress based on event progress and stage completion
        if (event.progress !== undefined) {
          // Map global progress to stage-specific progress
          if (stageId === "initialization") {
            // Initialization: 0-10% global progress
            stage.progress = Math.min(
              100,
              Math.max(0, (event.progress / 10) * 100)
            );
          } else if (stageId === "research") {
            // Research: 10-75% global progress (can extend with additional research)
            stage.progress = Math.min(
              100,
              Math.max(0, ((event.progress - 10) / 65) * 100)
            );
          } else if (stageId === "analysis") {
            // Analysis: 40-60% global progress
            stage.progress = Math.min(
              100,
              Math.max(0, ((event.progress - 40) / 20) * 100)
            );
          } else if (stageId === "report") {
            // Report: 80-100% global progress
            stage.progress = Math.min(
              100,
              Math.max(0, ((event.progress - 80) / 20) * 100)
            );
          }
        }

        // Ensure completed stages show 100% progress
        if (stage.status === "completed") {
          stage.progress = 100;
        }

        // Handle stage output from event data
        if (event.data) {
          if (typeof event.data === "object" && event.data.stage_output) {
            // Special handling for research stage to preserve detailed search summaries
            if (stageId === "research") {
              // Check if this is a search summary (contains "Search Results Summary")
              const isSearchSummary = event.data.stage_output.includes(
                "Search Results Summary"
              );
              const hasExistingSearchSummary =
                stage.output && stage.output.includes("Search Results Summary");

              if (isSearchSummary) {
                // Always use search summary as it's the most important output for research stage
                stage.output = event.data.stage_output;
                console.log("🔍 Search summary preserved in research stage:", {
                  stageId,
                  outputLength: event.data.stage_output.length,
                  hasSearchSummaries: !!event.data.search_summaries,
                  searchSummariesCount:
                    event.data.search_summaries?.length || 0,
                });
              } else if (!hasExistingSearchSummary) {
                // Only update if we don't already have a search summary
                stage.output = event.data.stage_output;
              }
              // If we already have a search summary and this isn't one, keep the existing one
            } else {
              // For other stages, normal update logic
              stage.output = event.data.stage_output;
            }
          } else if (typeof event.data === "string") {
            stage.output = event.data;
          } else {
            // For complex data objects, try to extract meaningful information
            if (
              event.data.search_summaries &&
              Array.isArray(event.data.search_summaries)
            ) {
              // If we have search summaries but no stage_output, generate a basic summary
              const summaries = event.data.search_summaries;
              const totalResults = summaries.reduce(
                (sum, s) => sum + (s.total_results || 0),
                0
              );
              const sources = [
                ...new Set(summaries.flatMap((s) => s.sources || [])),
              ];
              const domains = [
                ...new Set(summaries.flatMap((s) => s.domains || [])),
              ];

              stage.output = `## 🔍 Search Results Summary

### 📊 Overview
- **Total Results Found**: ${totalResults}
- **Information Sources**: ${sources.length} different sources
- **Websites Accessed**: ${domains.length} domains

### 🌐 Sources Used
${sources.join(", ") || "No sources available"}

### 🔗 Top Domains
${domains.slice(0, 5).join(", ") || "No domains available"}

---
✅ **Search completed successfully**`;
            } else {
              stage.output = JSON.stringify(event.data, null, 2);
            }
          }
        }
      }
    }
  });

  // Set previous stages to completed based on current progress
  // When entering report stage (85%+), all previous stages should be completed
  if (currentProgress >= 85) {
    const initStage = stages.find((s) => s.id === "initialization");
    if (
      initStage &&
      initStage.status !== "completed" &&
      initStage.status !== "error"
    ) {
      initStage.status = "completed";
      initStage.progress = 100;
    }

    const researchStage = stages.find((s) => s.id === "research");
    if (
      researchStage &&
      researchStage.status !== "completed" &&
      researchStage.status !== "error"
    ) {
      researchStage.status = "completed";
      researchStage.progress = 100;
    }

    const analysisStage = stages.find((s) => s.id === "analysis");
    if (
      analysisStage &&
      analysisStage.status !== "completed" &&
      analysisStage.status !== "error"
    ) {
      analysisStage.status = "completed";
      analysisStage.progress = 100;
    }
  }
  // When entering analysis stage (45%+), initialization and research should be completed
  else if (currentProgress >= 45) {
    const initStage = stages.find((s) => s.id === "initialization");
    if (
      initStage &&
      initStage.status !== "completed" &&
      initStage.status !== "error"
    ) {
      initStage.status = "completed";
      initStage.progress = 100;
    }

    const researchStage = stages.find((s) => s.id === "research");
    if (
      researchStage &&
      researchStage.status !== "completed" &&
      researchStage.status !== "error"
    ) {
      researchStage.status = "completed";
      researchStage.progress = 100;
    }
  }
  // When entering research stage (15%+), initialization should be completed
  else if (currentProgress >= 15) {
    const initStage = stages.find((s) => s.id === "initialization");
    if (
      initStage &&
      initStage.status !== "completed" &&
      initStage.status !== "error" &&
      // 确保只有在没有活动阶段时才自动完成初始化阶段
      !stages.some((s) => s.status === "active" && s.id === "initialization")
    ) {
      initStage.status = "completed";
      initStage.progress = 100;
    }
  }

  // When research is fully completed (100%), all stages should be completed
  if (currentProgress >= 100) {
    stages.forEach((stage) => {
      if (stage.status !== "error") {
        stage.status = "completed";
        stage.progress = 100;
      }
    });
  }

  return stages;
};

// Markdown component props type from former ReportView
type MdComponentProps = {
  className?: string;
  children?: ReactNode;
  [key: string]: any;
};

// Markdown components (from former ReportView.tsx)
const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn("text-2xl font-bold mt-4 mb-2", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn("text-xl font-bold mt-3 mb-2", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn("text-lg font-bold mt-3 mb-1", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn("mb-3 leading-7", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => (
    <Badge className="text-xs mx-0.5">
      <a
        className={cn("text-blue-400 hover:text-blue-300 text-xs", className)}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    </Badge>
  ),
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn("list-disc pl-6 mb-3", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn("list-decimal pl-6 mb-3", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn("mb-1", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote
      className={cn(
        "border-l-4 border-neutral-600 pl-4 italic my-3 text-sm",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code
      className={cn(
        "bg-neutral-900 rounded px-1 py-0.5 font-mono text-xs",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre
      className={cn(
        "bg-neutral-900 p-3 rounded-lg overflow-x-auto font-mono text-xs my-3",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn("border-neutral-600 my-4", className)} {...props} />
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn("border-collapse w-full", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th
      className={cn(
        "border border-neutral-600 px-3 py-2 text-left font-bold",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td
      className={cn("border border-neutral-600 px-3 py-2", className)}
      {...props}
    >
      {children}
    </td>
  ),
};

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: Message;
  mdComponents: typeof mdComponents;
}

// HumanMessageBubble Component
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  message,
  mdComponents,
}) => {
  return (
    <div
      className={`text-white rounded-3xl break-words min-h-7 bg-neutral-700 max-w-[100%] sm:max-w-[90%] px-4 pt-3 rounded-br-lg`}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
        {typeof message.content === "string"
          ? message.content
          : JSON.stringify(message.content)}
      </ReactMarkdown>
    </div>
  );
};

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  message: Message;
  historicalActivity: ProcessedEvent[] | undefined;
  liveActivity: ProcessedEvent[] | undefined;
  isLastMessage: boolean;
  isOverallLoading: boolean;
  mdComponents: typeof mdComponents;
  handleCopy: (text: string, messageId: string) => void;
  copiedMessageId: string | null;
}

// AiMessageBubble Component
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  message,
  historicalActivity,
  liveActivity,
  isLastMessage,
  isOverallLoading,
  mdComponents,
  handleCopy,
  copiedMessageId,
}) => {
  // Determine which activity events to show and if it's for a live loading message
  const activityForThisBubble =
    isLastMessage && isOverallLoading ? liveActivity : historicalActivity;
  const isLiveActivityForThisBubble = isLastMessage && isOverallLoading;

  return (
    <div className={`relative break-words flex flex-col `}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
        {typeof message.content === "string"
          ? message.content
          : JSON.stringify(message.content)}
      </ReactMarkdown>
      <Button
        variant="default"
        className="cursor-pointer bg-neutral-700 border-neutral-600 text-neutral-300 self-end"
        onClick={() =>
          handleCopy(
            typeof message.content === "string"
              ? message.content
              : JSON.stringify(message.content),
            message.id!
          )
        }
      >
        {copiedMessageId === message.id ? "Copied" : "Copy"}
        {copiedMessageId === message.id ? <CopyCheck /> : <Copy />}
      </Button>
    </div>
  );
};

interface ChatMessagesViewProps {
  messages: Message[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
  onSubmit: (
    inputValue: string,
    effort: string,
    model: string,
    searchEngine: string
  ) => void;
  onCancel: () => void;
  liveActivityEvents: ProcessedEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
  currentProgress?: number;
  currentStatus?: string;
  streamingReport?: string;
  isReportStreaming?: boolean;
  onShowDeepSearch?: () => void;
}

// New Research Interface Component
const ResearchInterface: React.FC<{
  query: string;
  stages: ResearchStage[];
  currentStage?: string;
  streamingReport: string;
  isReportStreaming: boolean;
  onCopy: (text: string) => void;
}> = ({
  query,
  stages,
  currentStage,
  streamingReport,
  isReportStreaming,
  onCopy,
}) => {
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(text);
      onCopy(text);
      setTimeout(() => setCopiedText(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  return (
    <div className="h-full flex flex-col bg-neutral-800 text-neutral-100 overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-neutral-700 p-2 bg-neutral-800"></div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden bg-neutral-800 min-h-0">
        {/* Left Sidebar - Stages */}
        <div className="w-80 border-r border-neutral-700 bg-neutral-900 flex-shrink-0">
          <ScrollArea className="h-full">
            <div className="p-4">
              <ResearchStagePanel stages={stages} currentStage={currentStage} />
            </div>
          </ScrollArea>
        </div>

        {/* Right Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden bg-neutral-800">
          {/* Scrollable Content Container */}

          <div className="p-6 space-y-6 ">
            {/* Stage Outputs Area */}
            {!isReportStreaming && (
              <div className="space-y-4">
                {/* Show stages with output in priority order */}
                {stages
                  .filter(
                    (stage) => stage.output && stage.output.trim().length > 0
                  )
                  .sort((a, b) => {
                    // Priority order: research (with search summary) > other completed > active
                    const aIsResearchWithSummary =
                      a.id === "research" &&
                      a.output?.includes("Search Results Summary");
                    const bIsResearchWithSummary =
                      b.id === "research" &&
                      b.output?.includes("Search Results Summary");

                    if (aIsResearchWithSummary && !bIsResearchWithSummary)
                      return -1;
                    if (!aIsResearchWithSummary && bIsResearchWithSummary)
                      return 1;

                    // Then by completion status
                    if (a.status === "completed" && b.status !== "completed")
                      return -1;
                    if (a.status !== "completed" && b.status === "completed")
                      return 1;

                    // Finally by stage order
                    const stageOrder = [
                      "initialization",
                      "research",
                      "analysis",
                      "report",
                    ];
                    return stageOrder.indexOf(a.id) - stageOrder.indexOf(b.id);
                  })
                  .map((stage) => (
                    <div key={`stage-output-${stage.id}`}>
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-medium text-neutral-100">
                          {stage.title} Output
                        </h2>
                        <div className="flex items-center gap-2">
                          {stage.status === "completed" && (
                            <span className="text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded">
                              ✓ Completed
                            </span>
                          )}
                          {stage.status === "active" && (
                            <span className="text-xs text-blue-400 bg-blue-400/10 px-2 py-1 rounded">
                              ⏳ In Progress
                            </span>
                          )}
                          {stage.id === "research" &&
                            stage.output?.includes(
                              "Search Results Summary"
                            ) && (
                              <span className="text-xs text-purple-400 bg-purple-400/10 px-2 py-1 rounded">
                                🔍 Search Summary
                              </span>
                            )}
                        </div>
                      </div>
                      <Card className="bg-neutral-900 border-neutral-700">
                        <CardContent className="p-4">
                          <div className="text-white prose prose-sm max-w-none prose-invert max-h-[60vh] overflow-y-auto">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {stage.output}
                            </ReactMarkdown>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  ))}

                {/* Show message if no outputs available */}
                {stages.filter(
                  (stage) => stage.output && stage.output.trim().length > 0
                ).length === 0 && (
                  <Card className="bg-neutral-900 border-neutral-700">
                    <CardContent className="p-4">
                      <div className="text-neutral-400 text-sm italic text-center">
                        {currentStage === "initialization"
                          ? "🚀 Initializing research process..."
                          : currentStage === "research"
                          ? "🔍 Collecting information..."
                          : currentStage === "analysis"
                          ? "🧠 Analyzing collected data..."
                          : currentStage === "report"
                          ? "📝 Generating final report..."
                          : "Waiting for research to begin..."}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}

            {/* Final Report Area */}
            {(streamingReport || isReportStreaming) && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-medium text-neutral-100">
                    Final Report
                  </h2>
                  {streamingReport && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopy(streamingReport)}
                      className="border-neutral-600 text-neutral-300 hover:bg-neutral-700"
                    >
                      {copiedText === streamingReport ? (
                        <>
                          <CopyCheck className="w-4 h-4 mr-2" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4 mr-2" />
                          Copy
                        </>
                      )}
                    </Button>
                  )}
                </div>
                <StreamingReport
                  content={streamingReport}
                  isStreaming={isReportStreaming}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  liveActivityEvents,
  historicalActivities,
  currentProgress = 0,
  currentStatus = "",
  streamingReport = "",
  isReportStreaming = false,
  onShowDeepSearch,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000); // Reset after 2 seconds
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  // Get the latest user query
  const latestUserMessage = messages.filter((m) => m.type === "human").pop();
  const query =
    typeof latestUserMessage?.content === "string"
      ? latestUserMessage.content
      : JSON.stringify(latestUserMessage?.content || "");

  // Convert events to stages
  const stages = convertEventsToStages(
    liveActivityEvents,
    currentStatus,
    currentProgress
  );

  // Determine current stage based on current status and events
  let currentStage = "";

  // First check for active stages in events
  const activeStage = stages.find((stage) => stage.status === "active");
  if (activeStage) {
    currentStage = activeStage.id;
  } else {
    // Fallback to status-based detection
    if (currentStatus.includes("init") || currentStatus.includes("start")) {
      currentStage = "initialization";
    } else if (
      currentStatus.includes("collect") ||
      currentStatus.includes("search") ||
      currentStatus.includes("research")
    ) {
      currentStage = "research";
    } else if (
      currentStatus.includes("analysis") ||
      currentStatus.includes("process")
    ) {
      currentStage = "analysis";
    } else if (
      currentStatus.includes("report") ||
      currentStatus.includes("generate")
    ) {
      currentStage = "report";
    }
  }

  // If we have an active research session, show the new interface
  if (isLoading || messages.some((m) => m.type === "human")) {
    return (
      <div className="flex flex-col h-full overflow-hidden">
        <div className="flex-1 overflow-hidden">
          <ResearchInterface
            query={query}
            stages={stages}
            currentStage={currentStage}
            streamingReport={streamingReport}
            isReportStreaming={isReportStreaming}
            onCopy={(text) => console.log("Copied:", text)}
          />
        </div>
        <div className="flex-shrink-0 border-t border-neutral-700 bg-neutral-800">
          <InputForm
            onSubmit={onSubmit}
            isLoading={isLoading}
            onCancel={onCancel}
            hasHistory={messages.length > 0}
            currentProgress={currentProgress}
            currentStatus={currentStatus}
            onShowDeepSearch={onShowDeepSearch}
          />
        </div>
      </div>
    );
  }

  // Fallback to original chat interface for backward compatibility
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 md:p-6 space-y-2 max-w-4xl mx-auto pt-16 max-h-[80vh] overflow-y-auto">
        {messages.map((message, index) => {
          const isLast = index === messages.length - 1;
          return (
            <div key={message.id || `msg-${index}`} className="space-y-3">
              <div
                className={`flex items-start gap-3 ${
                  message.type === "human" ? "justify-end" : ""
                }`}
              >
                {message.type === "human" ? (
                  <HumanMessageBubble
                    message={message}
                    mdComponents={mdComponents}
                  />
                ) : (
                  <AiMessageBubble
                    message={message}
                    historicalActivity={historicalActivities[message.id!]}
                    liveActivity={liveActivityEvents} // Pass global live events
                    isLastMessage={isLast}
                    isOverallLoading={isLoading} // Pass global loading state
                    mdComponents={mdComponents}
                    handleCopy={handleCopy}
                    copiedMessageId={copiedMessageId}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>

      <InputForm
        onSubmit={onSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={messages.length > 0}
        currentProgress={currentProgress}
        currentStatus={currentStatus}
        onShowDeepSearch={onShowDeepSearch}
      />
    </div>
  );
}
