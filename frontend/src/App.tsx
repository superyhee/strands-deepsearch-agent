import { useState, useEffect, useRef, useCallback } from "react";
import { ProcessedEvent } from "@/components/ActivityTimeline";
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { useResearchAgent, type Message } from "@/hooks/useResearchAgent";

export default function App() {
  const [processedEventsTimeline, setProcessedEventsTimeline] = useState<
    ProcessedEvent[]
  >([]);
  const [historicalActivities, setHistoricalActivities] = useState<
    Record<string, ProcessedEvent[]>
  >({});
  const [showDeepSearchInterface, setShowDeepSearchInterface] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const hasFinalizeEventOccurredRef = useRef(false);

  const apiUrl = import.meta.env.DEV
    ? "http://localhost:8001"
    : "http://localhost:8123";

  const researchAgent = useResearchAgent(apiUrl);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]"
      );
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [researchAgent.messages]);

  // Update progress events based on research agent status
  useEffect(() => {
    if (researchAgent.isLoading && researchAgent.lastStreamUpdate) {
      const update = researchAgent.lastStreamUpdate;
      const newEvent: ProcessedEvent = {
        title: update.message,
        data: update.data || { progress: researchAgent.currentProgress },
        progress: researchAgent.currentProgress,
        status:
          researchAgent.currentProgress === 100 ? "completed" : "processing",
        step: update.step || researchAgent.currentStep,
        stage: update.stage || researchAgent.currentStage,
      };

      setProcessedEventsTimeline((prev) => {
        // Check if this is a new status or an update to the last one
        if (
          prev.length === 0 ||
          prev[prev.length - 1].title !== newEvent.title
        ) {
          return [...prev, newEvent];
        } else {
          // Update the last event with new progress and data, but preserve important data
          const updated = [...prev];
          const lastEvent = updated[updated.length - 1];

          // Preserve detailed search summary data if it exists
          let preservedData = lastEvent.data;
          if (newEvent.data && typeof newEvent.data === "object") {
            // If the new event has stage_output with search summary, use it
            if (newEvent.data.stage_output) {
              preservedData = newEvent.data;
            } else if (
              lastEvent.data &&
              typeof lastEvent.data === "object" &&
              lastEvent.data.stage_output &&
              lastEvent.data.stage_output.includes("Search Results Summary")
            ) {
              // Keep the existing search summary data
              preservedData = lastEvent.data;
            } else {
              // For other cases, use the new data
              preservedData = newEvent.data;
            }
          }

          updated[updated.length - 1] = {
            ...newEvent,
            data: preservedData,
          };
          return updated;
        }
      });

      if (researchAgent.currentProgress === 100) {
        hasFinalizeEventOccurredRef.current = true;
      }
    }
  }, [
    researchAgent.lastStreamUpdate,
    researchAgent.currentProgress,
    researchAgent.isLoading,
  ]);

  useEffect(() => {
    if (
      hasFinalizeEventOccurredRef.current &&
      !researchAgent.isLoading &&
      researchAgent.messages.length > 0
    ) {
      const lastMessage =
        researchAgent.messages[researchAgent.messages.length - 1];
      if (lastMessage && lastMessage.type === "ai" && lastMessage.id) {
        setHistoricalActivities((prev) => ({
          ...prev,
          [lastMessage.id!]: [...processedEventsTimeline],
        }));
      }
      hasFinalizeEventOccurredRef.current = false;
    }
  }, [
    researchAgent.messages,
    researchAgent.isLoading,
    processedEventsTimeline,
  ]);

  const handleSubmit = useCallback(
    async (
      submittedInputValue: string,
      effort: string,
      model: string,
      searchEngine: string
    ) => {
      if (!submittedInputValue.trim()) return;
      setProcessedEventsTimeline([]);
      hasFinalizeEventOccurredRef.current = false;

      // convert effort to, initial_search_query_count and max_research_loops
      let initial_search_query_count = 0;
      let max_research_loops = 0;
      switch (effort) {
        case "low":
          initial_search_query_count = 1;
          max_research_loops = 1;
          break;
        case "medium":
          initial_search_query_count = 3;
          max_research_loops = 2;
          break;
        case "high":
          initial_search_query_count = 5;
          max_research_loops = 3;
          break;
      }

      const newMessages: Message[] = [
        ...(researchAgent.messages || []),
        {
          type: "human",
          content: submittedInputValue,
          id: Date.now().toString(),
        },
      ];

      await researchAgent.submit({
        messages: newMessages,
        initial_search_query_count: initial_search_query_count,
        max_research_loops: max_research_loops,
        search_engine: searchEngine,
      });
    },
    [researchAgent]
  );

  const handleCancel = useCallback(() => {
    researchAgent.stop();
    window.location.reload();
  }, [researchAgent]);

  const handleNewSearch = useCallback(() => {
    researchAgent.stop();
    window.location.reload();
  }, [researchAgent]);

  const handleShowDeepSearch = useCallback(() => {
    setShowDeepSearchInterface(true);
  }, []);

  return (
    <div className="flex flex-col h-screen bg-neutral-800 text-neutral-100 font-sans antialiased">
      <Header onNewSearch={handleNewSearch} />
      <main className="flex-1 flex flex-col overflow-hidden max-w-4xl mx-auto w-full">
        <div
          className={`flex-1 overflow-y-auto ${
            researchAgent.messages.length === 0 && !researchAgent.isLoading
              ? "flex"
              : ""
          }`}
        >
          {researchAgent.messages.length === 0 && !researchAgent.isLoading ? (
            <WelcomeScreen
              handleSubmit={handleSubmit}
              isLoading={researchAgent.isLoading}
              onCancel={handleCancel}
              currentProgress={researchAgent.currentProgress}
              currentStatus={researchAgent.currentStatus}
              onShowDeepSearch={handleShowDeepSearch}
            />
          ) : (
            <ChatMessagesView
              messages={researchAgent.messages}
              isLoading={researchAgent.isLoading}
              scrollAreaRef={scrollAreaRef}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              liveActivityEvents={processedEventsTimeline}
              historicalActivities={historicalActivities}
              currentProgress={researchAgent.currentProgress}
              currentStatus={researchAgent.currentStatus}
              streamingReport={researchAgent.streamingReport}
              isReportStreaming={researchAgent.isReportStreaming}
              onShowDeepSearch={handleShowDeepSearch}
            />
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
