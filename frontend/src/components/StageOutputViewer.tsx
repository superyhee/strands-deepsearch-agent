import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Clock, 
  Search, 
  BarChart3, 
  FileText, 
  Eye,
  EyeOff
} from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { StageOutput } from "@/hooks/useResearchAgent";

interface StageOutputViewerProps {
  stageOutputs: StageOutput[];
  selectedStage: string | null;
  onStageSelect: (stage: string | null) => void;
  currentStage?: string;
  className?: string;
}

const getStageIcon = (stage: string, status: string) => {
  const iconClass = cn(
    "w-4 h-4",
    status === "completed" ? "text-green-400" : 
    status === "active" ? "text-blue-400" : "text-gray-400"
  );

  switch (stage) {
    case "initialization":
      return <Clock className={iconClass} />;
    case "research":
      return <Search className={iconClass} />;
    case "analysis":
      return <BarChart3 className={iconClass} />;
    case "report":
      return <FileText className={iconClass} />;
    default:
      return <Clock className={iconClass} />;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "completed":
      return <Badge variant="default" className="bg-green-600 text-white">Completed</Badge>;
    case "active":
      return <Badge variant="default" className="bg-blue-600 text-white">Processing</Badge>;
    case "pending":
      return <Badge variant="secondary">Pending</Badge>;
    case "error":
      return <Badge variant="destructive">Error</Badge>;
    default:
      return <Badge variant="secondary">{status}</Badge>;
  }
};

export const StageOutputViewer: React.FC<StageOutputViewerProps> = ({
  stageOutputs,
  selectedStage,
  onStageSelect,
  currentStage,
  className
}) => {
  const [showFullContent, setShowFullContent] = useState(false);

  if (stageOutputs.length === 0) {
    return (
      <Card className={cn("bg-neutral-900 border-neutral-700", className)}>
        <CardContent className="p-6 text-center text-neutral-400">
          <Clock className="w-8 h-8 mx-auto mb-2" />
          <p>等待研究阶段输出...</p>
        </CardContent>
      </Card>
    );
  }

  const selectedStageData = selectedStage 
    ? stageOutputs.find(s => s.stage === selectedStage)
    : null;

  return (
    <div className={cn("space-y-4", className)}>
      {/* Stage Selection Tabs */}
      <Card className="bg-neutral-900 border-neutral-700">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg text-neutral-100 flex items-center gap-2">
            <Eye className="w-5 h-5" />
            研究阶段输出
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedStage || ""} onValueChange={onStageSelect}>
            <TabsList className="grid w-full grid-cols-4 bg-neutral-800">
              {stageOutputs.map((stage) => (
                <TabsTrigger
                  key={stage.stage}
                  value={stage.stage}
                  className={cn(
                    "flex items-center gap-2 text-xs",
                    stage.stage === currentStage && "ring-2 ring-blue-500"
                  )}
                >
                  {getStageIcon(stage.stage, stage.status)}
                  <span className="hidden sm:inline">{stage.title}</span>
                </TabsTrigger>
              ))}
            </TabsList>

            {/* Stage Content */}
            {stageOutputs.map((stage) => (
              <TabsContent key={stage.stage} value={stage.stage} className="mt-4">
                <Card className="bg-neutral-800 border-neutral-600">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getStageIcon(stage.stage, stage.status)}
                        <CardTitle className="text-base text-neutral-100">
                          {stage.title}
                        </CardTitle>
                        {getStatusBadge(stage.status)}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowFullContent(!showFullContent)}
                          className="text-neutral-400 hover:text-neutral-200"
                        >
                          {showFullContent ? (
                            <>
                              <EyeOff className="w-4 h-4 mr-1" />
                              简化视图
                            </>
                          ) : (
                            <>
                              <Eye className="w-4 h-4 mr-1" />
                              完整内容
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                    <p className="text-xs text-neutral-500">
                      {new Date(stage.timestamp).toLocaleString('zh-CN')}
                    </p>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-96 w-full">
                      <div className="prose prose-sm max-w-none prose-invert">
                        <ReactMarkdown>
                          {showFullContent ? stage.fullContent : stage.content}
                        </ReactMarkdown>
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Quick Stage Overview */}
      <Card className="bg-neutral-900 border-neutral-700">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-neutral-300">阶段概览</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {stageOutputs.map((stage) => (
              <Button
                key={stage.stage}
                variant={selectedStage === stage.stage ? "default" : "ghost"}
                size="sm"
                onClick={() => onStageSelect(stage.stage)}
                className={cn(
                  "flex flex-col items-center gap-1 h-auto py-3",
                  selectedStage === stage.stage 
                    ? "bg-blue-600 hover:bg-blue-700" 
                    : "hover:bg-neutral-800",
                  stage.stage === currentStage && "ring-2 ring-blue-500"
                )}
              >
                {getStageIcon(stage.stage, stage.status)}
                <span className="text-xs">{stage.title}</span>
                {getStatusBadge(stage.status)}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default StageOutputViewer;
