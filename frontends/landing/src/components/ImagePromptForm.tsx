import { useState } from "react";

function ImagePromptForm() {
  const [prompt, setPrompt] = useState("");
  const [width, setWidth] = useState(1024);
  const [height, setHeight] = useState(1024);
  const [guidanceScale, setGuidanceScale] = useState(7.0);
  const [seed, setSeed] = useState(0);

  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await fetch("/api/images", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          width,
          height,
          guidance_scale: guidanceScale,
          seed,
        }),
      });

      if (!response.ok) throw new Error("Failed to generate image");
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-5 max-w-md mx-auto shadow-lg rounded-lg">
      <input
        type="text"
        placeholder="Enter image prompt..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={isLoading}
        className="input input-bordered w-full"
      />

      <div className="grid grid-cols-2 gap-4 mt-4">
        <label className="flex flex-col">
          <span className="text-sm font-medium">Width (px)</span>
          <input
            type="number"
            value={width}
            onChange={(e) => setWidth(Number(e.target.value))}
            disabled={isLoading}
            className="input input-bordered"
          />
        </label>
        <label className="flex flex-col">
          <span className="text-sm font-medium">Height (px)</span>
          <input
            type="number"
            value={height}
            onChange={(e) => setHeight(Number(e.target.value))}
            disabled={isLoading}
            className="input input-bordered"
          />
        </label>
      </div>

      <div className="mt-4">
        <label className="flex flex-col">
          <span className="text-sm font-medium">Guidance Scale: {guidanceScale}</span>
          <input
            type="range"
            min={0.1}
            max={20.0}
            step={0.1}
            value={guidanceScale}
            onChange={(e) => setGuidanceScale(Number(e.target.value))}
            className="range range-primary"
          />
        </label>
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading || !prompt}
        className="mt-4 btn btn-primary w-full disabled:btn-secondary"
      >
        {isLoading ? "Generating..." : "Generate Image"}
      </button>

      {error && <p className="text-red-500 text-sm mt-2">{error.message}</p>}
    </div>
  );
}

export default ImagePromptForm;
