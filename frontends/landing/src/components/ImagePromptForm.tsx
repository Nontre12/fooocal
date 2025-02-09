import { useState } from "react";

function ImagePromptForm() {
  const [prompt, setPrompt] = useState("");
  const [width, setWidth] = useState<number>(1024);
  const [height, setHeight] = useState<number>(1024);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      const response = await fetch("/api/images", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          "prompt": prompt,
          "width": width,
          "height": height
        })
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
      <div className="flex gap-2 mt-2">
        <input
          type="number"
          value={width}
          onChange={(e) => setWidth(Number(e.target.value))}
          disabled={isLoading}
          className="text-black w-1/2 px-3 py-2 border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-200"
          placeholder="Width"
        />
        <input
          type="number"
          value={height}
          onChange={(e) => setHeight(Number(e.target.value))}
          disabled={isLoading}
          className="text-black w-1/2 px-3 py-2 border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-200"
          placeholder="Height"
        />
      </div>
      <button
        onClick={handleSubmit}
        disabled={isLoading || !prompt}
        className="mt-2 btn btn-primary disabled:btn-secondary"
      >
        {isLoading ? "Generating..." : "Generate Image"}
      </button>
      {error && <p className="text-red-500 text-sm">{error.message}</p>}
    </div>
  );
}

export default ImagePromptForm;
