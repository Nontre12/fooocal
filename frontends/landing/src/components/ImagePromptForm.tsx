import React, { useEffect, useState } from "react";

interface ImageData {
  _id: string;
  image_file_name: string;
  status: string;
}

const ImagePromptForm: React.FC = () => {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [images, setImages] = useState<ImageData[]>([]);
  const [fetching, setFetching] = useState<boolean>(true);

  useEffect(() => {
    async function fetchImages() {
      try {
        const response = await fetch("/api/images");
        const data = await response.json();
        setImages(data);
      } catch (error) {
        console.error("Error fetching images:", error);
      } finally {
        setFetching(false);
      }
    }
    fetchImages();
  }, [loading]);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/images", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate image");
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 p-4 border rounded-lg shadow-md max-w-md mx-auto">
      <input
        type="text"
        placeholder="Enter image prompt..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={loading}
        className="w-full px-3 py-2 border rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-200"
      />
      <button
        onClick={handleSubmit}
        disabled={loading || !prompt}
        className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? "Generating..." : "Generate Image"}
      </button>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {fetching ? (
        <div>Loading...</div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {images.length === 0 ? (
            <p>No images available</p>
          ) : (
            images.map((item) => (
              <div key={item.image_file_name}>
                <img
                  src={`/images/${item.image_file_name}`}
                  alt={item.image_file_name}
                  className="image"
                />
                <span className="text-white">{item.status}</span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ImagePromptForm;
