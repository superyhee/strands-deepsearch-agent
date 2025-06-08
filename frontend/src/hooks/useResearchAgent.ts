import { useState, useCallback } from "react";

export interface Message {
  type: "human" | "ai";
  content: string;
  id: string;
}

export interface ResearchRequest {
  messages: Message[];
  max_research_loops: number;
  initial_search_query_count: number;
}

export interface ResearchResponse {
  messages: Message[];
  sources_gathered: Array<{
    label: string;
    value: string;
    short_url: string;
  }>;
  research_metadata: {
    research_loops: number;
    timestamp: string;
    query: string;
  };
}

export interface StreamUpdate {
  type:
    | "status"
    | "progress"
    | "complete"
    | "error"
    | "report_start"
    | "report_chunk";
  message: string;
  progress?: number;
  step?: string;
  stage?: string;
  data?: any;
  error?: string;
}

export interface UseResearchAgentReturn {
  messages: Message[];
  isLoading: boolean;
  currentProgress: number;
  currentStatus: string;
  currentStep: string;
  currentStage: string;
  streamingReport: string;
  isReportStreaming: boolean;
  lastStreamUpdate: StreamUpdate | null;
  submit: (data: ResearchRequest) => Promise<void>;
  stop: () => void;
}

export function useResearchAgent(apiUrl: string): UseResearchAgentReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [currentStatus, setCurrentStatus] = useState("");
  const [currentStep, setCurrentStep] = useState("");
  const [currentStage, setCurrentStage] = useState("");
  const [streamingReport, setStreamingReport] = useState("");
  const [isReportStreaming, setIsReportStreaming] = useState(false);
  const [lastStreamUpdate, setLastStreamUpdate] = useState<StreamUpdate | null>(
    null
  );
  const [abortController, setAbortController] =
    useState<AbortController | null>(null);
  const [eventSource, setEventSource] = useState<EventSource | null>(null);

  const submit = useCallback(
    async (data: ResearchRequest) => {
      setIsLoading(true);
      setCurrentProgress(0);
      setCurrentStatus("Prepare to research...");

      // Create abort controller for cancellation
      const controller = new AbortController();
      setAbortController(controller);

      try {
        // Convert message format from frontend to backend
        const backendMessages = data.messages.map((msg) => ({
          role: msg.type === "human" ? "user" : "assistant",
          content: msg.content,
        }));

        const backendRequest = {
          messages: backendMessages,
          max_research_loops: data.max_research_loops,
          initial_search_query_count: data.initial_search_query_count,
        };

        // Create EventSource for streaming
        const queryParams = new URLSearchParams({
          messages: JSON.stringify(backendRequest.messages),
          max_research_loops: backendRequest.max_research_loops.toString(),
          initial_search_query_count:
            backendRequest.initial_search_query_count.toString(),
        });

        // Use POST request for streaming
        const response = await fetch(`${apiUrl}/research`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          body: JSON.stringify(backendRequest),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        if (!response.body) {
          throw new Error("Response body is null");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split("\n");

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.slice(6));
                  handleStreamUpdate(data);
                } catch (e) {
                  console.error("Error parsing stream data:", e);
                }
              }
            }
          }
        } finally {
          reader.releaseLock();
        }
      } catch (error) {
        if (error instanceof Error && error.name === "AbortError") {
          console.log("Request was cancelled");
          setCurrentStatus("Request cancelled");
        } else {
          console.error("Research request failed:", error);
          setCurrentStatus("Research request failed");
          // Add error message to chat
          const errorMessage: Message = {
            type: "ai",
            content:
              "Sorry, an error occurred while processing your request. Please try again.",
            id: Date.now().toString(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
      } finally {
        setIsLoading(false);
        setAbortController(null);
      }
    },
    [apiUrl]
  );

  const handleStreamUpdate = useCallback((update: StreamUpdate) => {
    setLastStreamUpdate(update);
    setCurrentStatus(update.message);

    if (update.progress !== undefined) {
      setCurrentProgress(update.progress);
    }

    if (update.step) {
      setCurrentStep(update.step);
    }

    // Extract stage from update or data
    if (update.stage) {
      setCurrentStage(update.stage);
    } else if (
      update.data &&
      typeof update.data === "object" &&
      update.data.stage
    ) {
      setCurrentStage(update.data.stage);
    } else if (update.step) {
      // Map step to stage
      if (update.step === "initialization") {
        setCurrentStage("initialization");
      } else if (
        update.step.includes("research") ||
        update.step.includes("additional_research")
      ) {
        setCurrentStage("research");
      } else if (update.step.includes("analysis")) {
        setCurrentStage("analysis");
      } else if (
        update.step.includes("report") ||
        update.step === "final_report" ||
        update.step === "report_streaming" ||
        update.step === "report_streaming_start"
      ) {
        setCurrentStage("report");
      }
    }

    if (update.type === "report_start") {
      // Start streaming report
      setIsReportStreaming(true);
      setStreamingReport("");
    } else if (update.type === "report_chunk" && update.data?.chunk) {
      // Add chunk to streaming report
      setStreamingReport((prev) => prev + update.data.chunk);
    } else if (update.type === "complete" && update.data) {
      // Research completed, add final message
      setIsLoading(false); // Set loading to false when research is complete
      setIsReportStreaming(false);
      const finalMessage: Message = {
        type: "ai",
        content: update.data.final_report,
        id: Date.now().toString(),
      };
      setMessages((prev) => [...prev, finalMessage]);
      setCurrentStatus("Research completed!");
      setCurrentProgress(100);
      setStreamingReport(""); // Clear streaming report
    } else if (update.type === "error") {
      setIsLoading(false); // Set loading to false on error
      setIsReportStreaming(false);
      const errorMessage: Message = {
        type: "ai",
        content: `Error during research: ${update.message}`,
        id: Date.now().toString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setCurrentStatus("Research failed");
      setStreamingReport(""); // Clear streaming report
    }
  }, []);

  const stop = useCallback(() => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsLoading(false);
    }
    if (eventSource) {
      eventSource.close();
      setEventSource(null);
    }
    setCurrentStatus("Stopped");
  }, [abortController, eventSource]);

  return {
    messages,
    isLoading,
    currentProgress,
    currentStatus,
    currentStep,
    currentStage,
    streamingReport,
    isReportStreaming,
    lastStreamUpdate,
    submit,
    stop,
  };
}
