import React, { ChangeEvent, useState } from "react";
import { Input } from "../components/ui/input";
import { Separator } from "../components/ui/separator";
import Autoplay from "embla-carousel-autoplay";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "../components/ui/carousel";
import { Loader } from "../components/custom/loader";
import { tree, BASE_URL, allowedFileTypes, MAX_FILE_SIZE } from "../lib/constants";

const ImageSearch: React.FC = () => {
  const [error, setError] = useState("");
  const [message, setMessage] = useState("Please upload an image to view similar images here");
  const [showLoader, setShowLoader] = useState(false);
  const [disableUploadButton, setDisableUploadButton] = useState(false);
  const [similarImages, setSimilarImages] = useState([] as string[]);
  const [selectedImage, setSelectedImage] = useState<string | null>(tree);

  const handleImageUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    event.preventDefault();
  
    const file = event.target.files?.[0];
    if (!file) {
      setError("Please select an image");
      return;
    }
  
    if (!allowedFileTypes.includes(file.type)) {
      setError("Invalid file type. Please select a JPEG or PNG image.");
      return;
    }
  
    if (file.size > MAX_FILE_SIZE) {
      setError('File size is greater than max limit of 2 MB.');
      return;
    }
  
    setShowLoader(true);
    setDisableUploadButton(true);
    setError('');
  
    const formData = new FormData();
    formData.append("file", file);
    
    setSelectedImage(URL.createObjectURL(file));
  
    try {
      const response = await fetch(`${BASE_URL}/images/similar`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
  
      if (data && data.results && Array.isArray(data.results) && data.results.length) {
        const similarImages = data.results.map((result: { image_url: string }) => result.image_url);
        setSimilarImages(similarImages);
        setMessage("");
      } else {
        setMessage("No similar images found.");
      }
    } catch (error) {
      setError('An error occurred while uploading the image. Please try again.');
      setMessage('');
    } finally {
      setShowLoader(false);
      setDisableUploadButton(false);
      event.target.value = '';
    }
  };
  

  return (
    <div className="rounded-2xl p-5 m-5 flex flex-col items-center justify-center">
      <p className="p-5 text-2xl">Upload an image to view similar images</p>
      {selectedImage && (
        <img
          className="max-h-[500px] max-w-[500px] rounded-2xl"
          src={selectedImage}
          alt="Image"
        />
      )}
      <Input
        className="rounded-full w-1/2 cursor-pointer mt-5 text-center"
        id="picture"
        type="file"
        onChange={handleImageUpload}
        disabled={disableUploadButton}
      />
      {error && <p className="text-center text-rose-600 pt-2">{error}</p>}
      <Separator className="bg-black mt-5" />
      <p className="p-5 text-2xl">Similar Images</p>


      {showLoader ? (
        <Loader />
      ) : message ? (
        <p className="text-center pt-2">{message}</p>
      ) : (
        <Carousel
          plugins={[Autoplay({ delay: 2000 })]}
          opts={{ align: "start", loop: true }}
          className="w-full max-w-[500px] rounded-2xl"
        >
          <CarouselContent>
          {similarImages && similarImages.map((image: string, index: number) => (
              <CarouselItem key={index}>
                <img className="rounded-2xl" src={image} alt="Image" />
              </CarouselItem>
            ))}
          </CarouselContent>
        </Carousel>
      )}
    </div>
  );
};

export default ImageSearch;
