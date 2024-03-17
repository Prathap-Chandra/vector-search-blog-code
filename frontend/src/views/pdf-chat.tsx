import React, { useState } from "react";
import { Separator } from "../components/ui/separator";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { MAX_FILE_SIZE, BASE_URL } from "../lib/constants";

const PDFChat: React.FC = () => {
  const items = Array.from({ length: 10 });
  const [userQuery, setUserQuery] = useState("");
  const [uploadError, setUploadError] = useState('');
  const [error, setError] = useState("");

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      setUploadError('Please upload a PDF.');
      return;
    }

    // Checking for a non-PDF file
    if (file.type !== 'application/pdf') {
      setUploadError('Unsupported file type. Please upload a PDF.');
      return;
    }

    // Checking for file size exceeding limit
    if (file.size > MAX_FILE_SIZE) {
      setUploadError('File size is greater than max limit of 2 MB.');
      return;
    }

    // Resetting the error in case of a successful validation
    setUploadError('');

    const formData = new FormData();
    formData.append("file", file);

    fetch(`${BASE_URL}/hello`, {
      method: "GET",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
      })
      .catch((error) => {
        console.error(error);
        // handle this according to the error
        setUploadError('An error occurred while uploading the file. Please try again.');
      });
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!userQuery || userQuery.trim() === "") {
      setError("Please enter your query before submitting");
      return;
    }

    setUserQuery("");
    setError("");

    fetch("http://localhost:5000/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
      })
      .catch((error) => {
        // Handle any error that occurred during the API call
        console.error(error);
      });
  }

  return (
    <div className="bg-slate-600 rounded-2xl p-5 m-5 flex flex-col items-center align-middle justify-center">
      <div className="text-2xl">Upload a PDF to chat with it</div>
      <Separator className="bg-black mt-3 mb-3" />
      {items.map((_, index) => (
        <React.Fragment key={index}>
          <div className="flex flex-row justify-start">
            <div className="max-w-1/2">
              <img
                src="https://seeklogo.com/images/C/chatgpt-logo-02AFA704B5-seeklogo.com.png"
                className="max-w-[30px] max-h-[30px]"
                alt=""
              />
            </div>
            <div className="max-w-1/2 pl-4">
              Welcome! I'm a specialized chatbot here to assist you with content directly from your own PDFs. Simply upload any PDF document, and feel free to ask me questions based on the information within those files. Please note that my answers will be limited to the content of your uploaded PDFs. I'm ready whenever you are, so go ahead and upload a document to get started!
            </div>
          </div>
          <Separator className="bg-black mt-3 mb-3" />
        </React.Fragment>
      ))}

      <div className="flex flex-row items-center justify-center align-middle w-full">
        <Label className="text-md pr-5">Click the button to upload a PDF</Label>
        <Input
          className="rounded-full max-w-[280px] cursor-pointer text-center"
          id="picture"
          type="file"
          onChange={handleFileUpload}
        />
        {uploadError && <p>{uploadError}</p>}
      </div>
      <Separator className="bg-black mt-3" />
      
      <form
        onSubmit={handleSubmit}
        className="flex flex-row items-center justify-center align-middle w-full"
      >
        <Textarea
          onChange={(e) => setUserQuery(e.target.value)}
          className="w-full rounded-xl mt-5"
          placeholder="Enter your prompt here."
        />
        <Button
          variant="outline"
          type="submit"
          className="text-lg ml-4 mt-4 p-5 rounded-full"
        >
          Submit
        </Button>
      </form>

      <div className="flex flex-row items-center justify-center align-middle w-full pt-2">
        {error && <p>{error}</p>}
      </div>
    </div>
  );
};

export default PDFChat;
