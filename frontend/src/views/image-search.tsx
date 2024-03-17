import React, { ChangeEvent, useState } from "react";
import { Input } from "../components/ui/input";
import { Separator } from "../components/ui/separator";
import Autoplay from "embla-carousel-autoplay";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "../components/ui/carousel";
import { Loader } from "../components/custom/loader";

const ImageSearch: React.FC = () => {
  const [loader] = useState(true);
  
  const [images] = useState([
    "https://cdnph.upi.com/collection/fp/upi/13204/84e9840e6836c43d1721d0cc45b4ff8b/Liam-Neeson-turns-70-a-look-back_16_1.jpg",
    "https://cdnph.upi.com/collection/fp/upi/13204/84e9840e6836c43d1721d0cc45b4ff8b/Liam-Neeson-turns-70-a-look-back_16_1.jpg",
    "https://cdnph.upi.com/collection/fp/upi/13204/84e9840e6836c43d1721d0cc45b4ff8b/Liam-Neeson-turns-70-a-look-back_16_1.jpg",
    "https://cdnph.upi.com/collection/fp/upi/13204/84e9840e6836c43d1721d0cc45b4ff8b/Liam-Neeson-turns-70-a-look-back_16_1.jpg",
    "https://cdnph.upi.com/collection/fp/upi/13204/84e9840e6836c43d1721d0cc45b4ff8b/Liam-Neeson-turns-70-a-look-back_16_1.jpg",
  ]);

  const [selectedImage, setSelectedImage] = useState<string | null>(
    "https://cdnph.upi.com/collection/fp/upi/13204/84e9840e6836c43d1721d0cc45b4ff8b/Liam-Neeson-turns-70-a-look-back_16_1.jpg"
  );

  const handleImageUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = async () => {
        setSelectedImage(reader.result as string);
        reader.readAsDataURL(file);

        // Make the API call here
        try {
          const response = await fetch("your-api-endpoint", {
            method: "POST",
            body: file,
            headers: {
              "Content-Type": file.type,
            },
          });

          // Handle the response
          if (response.ok) {
            // API call successful
            // Do something with the response data
          } else {
            // API call failed
            // Handle the error
          }
        } catch (error) {
          // Handle any network or other errors
        }
      };
    }
  };

  return (
    <div className="bg-slate-600 rounded-2xl p-5 m-5 flex flex-col items-center justify-center">
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
      />
      <Separator className=" bg-black mt-5" />
      <p className="p-5 text-2xl">View similar images</p>

      {loader && ( <Loader /> )} 
      <Carousel
        plugins={[Autoplay({ delay: 2000 })]}
        opts={{ align: "start", loop: true }}
        className="w-full max-w-[420px] rounded-2xl"
      >
        <CarouselContent>
          {Array.from({ length: 5 }).map((_, index) => (
            <CarouselItem key={index}>
              <img
                className="rounded-2xl"
                src={images[index + 1]}
                alt="Image"
              />
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
    </div>
  );
};

export default ImageSearch;
