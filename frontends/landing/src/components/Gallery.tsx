import { useState, useEffect } from "react";

interface ImageData {
  _id: string;
  image_file_name: string;
  status: string;
}

const getImages = async () => {
  const response = await fetch("/api/images");
  return response.json();
};

function Gallery() {
  const [data, setData] = useState<ImageData[] | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let intervalId: number | null = null;

    const fetchData = async () => {
      try {
        const images = await getImages();
        setData(images);

        if (images.every((img: ImageData) => img.status === "DONE")) {
          if (intervalId) clearInterval(intervalId);
        }
      } catch (err) {
        setError(err as Error);
        if (intervalId) clearInterval(intervalId);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
    intervalId = setInterval(fetchData, 3000);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  if (error) return <div>Failed to load</div>;
  if (isLoading)
    return (
      <div className="flex min-h-screen items-center justify-center">
        <span className="loading loading-spinner loading-xl"></span>
      </div>
    );
  if (!data || data.length === 0) return <div>No images found</div>;

  return (
    <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 p-4">
      {data.map((value) => (
        <div key={value._id} className="mb-4 break-inside-avoid overflow-hidden rounded-lg shadow-lg">
          {value.status === "DONE" ? (
            <img
              src={`/images/${value.image_file_name}`}
              alt={value.image_file_name}
              loading="lazy"
              className="w-full h-auto object-cover rounded-lg"
            />
          ) : (
            <div className="flex h-32 w-full items-center justify-center bg-gray-200 rounded-lg">
              <span className="loading loading-spinner loading-xl"></span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default Gallery;
