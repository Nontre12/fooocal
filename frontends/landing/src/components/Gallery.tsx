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
    const fetchData = async () => {
      try {
        const images = await getImages();
        setData(images);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
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
    <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {data.map((value) => (
        <div key={value._id} className="h-auto max-w-full rounded-lg flex items-center justify-center">
          {value.status === "DONE" ? (
            <img src={`/images/${value.image_file_name}`} alt={value.image_file_name} loading="lazy" />
          ) : (
            <div className="flex h-32 w-32 items-center justify-center">
              <span className="loading loading-spinner loading-xl"></span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default Gallery;