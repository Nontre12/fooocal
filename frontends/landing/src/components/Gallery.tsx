import React, { useEffect, useState } from 'react';

interface ImageData {
  image_file_name: string;
}

const Gallery: React.FC = () => {
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchImages() {
      try {
        const response = await fetch('/api/images');
        const data = await response.json();

        setImages(data);
      } catch (error) {
        console.error('Error fetching images:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchImages();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="image-grid">
      {images.length === 0 ? (
        <p>No images available</p>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          {images.map((item) => (
            <div key={item.image_file_name}>
              <img
                src={`/images/${item.image_file_name}`}
                alt={item.image_file_name}
                className="image"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Gallery;
