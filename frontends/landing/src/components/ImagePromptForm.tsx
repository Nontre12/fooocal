import { useState } from "react";

function ImagePromptForm() {
  const [prompt, setPrompt] = useState("");
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setIsLoading(false);
      const response = await fetch("/api/images", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate image");
      }
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-5">
      <input
        type="text"
        placeholder="Enter image prompt..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={isLoading}
        className="text-black w-full px-3 py-2 border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-200"
      />
      <button
        onClick={handleSubmit}
        disabled={isLoading || !prompt}
        className="mt-2 btn btn-primary disabled:btn-secondary"
      >
        {isLoading ? "Generating..." : "Generate Image"}
      </button>
      {error && <p className="text-red-500 text-sm">{error}</p>}
    </div>
  );
};

export default ImagePromptForm;
