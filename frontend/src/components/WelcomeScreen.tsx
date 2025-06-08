import { InputForm } from "./InputForm";
import { Progress } from "./ui/progress";

interface WelcomeScreenProps {
  handleSubmit: (
    submittedInputValue: string,
    effort: string,
    model: string,
    searchEngine: string
  ) => void;
  onCancel: () => void;
  isLoading: boolean;
  currentProgress?: number;
  currentStatus?: string;
  onShowDeepSearch?: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  handleSubmit,
  onCancel,
  isLoading,
  currentProgress = 0,
  currentStatus = "",
  onShowDeepSearch,
}) => (
  <div className="flex flex-col items-center justify-center text-center px-4 flex-1 w-full max-w-3xl mx-auto gap-4">
    <div>
      <h1 className="text-5xl md:text-6xl font-semibold text-neutral-100 mb-3">
        Welcome.
      </h1>
      <p className="text-xl md:text-2xl text-neutral-400">
        How can I help you today?
      </p>
    </div>

    {/* Progress indicator when loading */}
    {isLoading && (
      <div className="w-full max-w-md space-y-3">
        <div className="text-sm text-neutral-300 font-medium">
          {currentStatus || "Processing your request..."}
        </div>
        <Progress value={currentProgress} className="w-full" />
        <div className="text-xs text-neutral-500">
          {currentProgress}% Complete
        </div>
      </div>
    )}

    <div className="w-full mt-4">
      <InputForm
        onSubmit={handleSubmit}
        isLoading={isLoading}
        onCancel={onCancel}
        hasHistory={false}
        currentProgress={currentProgress}
        currentStatus={currentStatus}
        onShowDeepSearch={onShowDeepSearch}
      />
    </div>
  </div>
);
