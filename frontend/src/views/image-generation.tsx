import React, { useState } from "react";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { beach, BASE_URL } from "../lib/constants";
import { apiRequest } from "../lib/utils";
import { Loader } from "../components/custom/loader";

function ImageGeneration() {
  const [prompt, setPrompt] = useState("");
  const [error, setError] = useState("");
  const [showLoader, setShowLoader] = useState(false);
  const [disableSubmitButton, setDisableSubmitButton] = useState(false);

  const [selectedImage, setSelectedImage] = useState<string | null>(beach);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();

    if (prompt.trim() === "") {
      setError("Please enter a Prompt");
      return;
    }

    try {
      // Reset form
      setPrompt("");
      setError("");

      setShowLoader(true);
      setDisableSubmitButton(true);

      const response = await apiRequest(`${BASE_URL}/images/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: { 'image-description': prompt },
        json: true,
      });

      await new Promise((resolve) => setTimeout(resolve, 5000)); // Add a 5-second delay

      if (response && response.image_url) {
        setSelectedImage(response.image_url);
      } else {
        setError("An error occurred while generating the image. Please try again.");
      }

    } catch (error) {
      setError("An error occurred while generating the image. Please try again.");
    }

    setShowLoader(false);
    setDisableSubmitButton(false);
  };

  return (
    <div className=" rounded-2xl p-5 m-5 flex flex-col items-center justify-center">
      <p className="text-xl pb-3">Generating an image might take anywhere between 2 to 10 mins depending on your hardware.</p>
      {showLoader ? (
        <Loader />
      ) : (
        <>
        {selectedImage && (
          <img
            className="max-h-[560px] max-w-[1000px] rounded-2xl"
            src={selectedImage}
            alt="Image"
          />
        )}
        </>
      )}  
      
      <form
        onSubmit={handleSubmit}
        className="flex flex-col items-center justify-center"
      >
        <Textarea
          onChange={(e) => setPrompt(e.target.value)}
          className="w-[500px] rounded-xl mt-5"
          placeholder="Enter your prompt here."
          value={prompt}
        />
        {error && <p className="text-rose-600 pt-2">{error}</p>}
        <Button
          variant="outline"
          type="submit"
          className="text-lg mt-3 p-5 rounded-full disabled"
          disabled={disableSubmitButton}
        >
          Submit
        </Button>
      </form>
    </div>
  );
}

export default ImageGeneration;
