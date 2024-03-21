import React, { ChangeEvent, FormEvent, useState } from "react";
import { Separator } from "../components/ui/separator";
import { Textarea } from "../components/ui/textarea";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { MAX_FILE_SIZE, BASE_URL, gptLogo } from "../lib/constants";

const PDFChat: React.FC = () => {
  const [userQuery, setUserQuery] = useState("");
  const [submitMessage, setSubmitMessage] = useState("");
  const [fileUploadMessage, setFileUploadMessage] = useState("");
  const [disableButtons, setDisableButtons] = useState(false);
  const [conversation, updateConversation] = useState([
    {
      role: "Bot",
      message: "Welcome! I'm a specialized chatbot here to assist you with content directly from your own PDFs. Simply upload any PDF document, and feel free to ask me questions based on the information within those files. Please note that my answers will be limited to the content of your uploaded PDFs. I'm ready whenever you are, so go ahead and upload a document to get started!",
    },
  ]);

  const handleFileUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const fileInput = event.target;
    const file = fileInput.files?.[0];
    setFileUploadMessage('');

    try {
      const formData = new FormData();

      if (!file) {
        setFileUploadMessage('No file selected.');
        return;
      }

      if (file.type !== 'application/pdf') {
        setFileUploadMessage('Unsupported file type. Please upload a PDF.');
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        setFileUploadMessage('File size is greater than max limit of 2 MB.');
        return;
      }

      formData.append("file", file);
      setDisableButtons(true);

      setFileUploadMessage('Please wait while we upload your file.');
      
      await fetch(`${BASE_URL}/conversation/attachment`, { method: "POST", body: formData });
      setFileUploadMessage('File uploaded successfully. You can now ask questions based on the content of the PDF.');
    } catch (error) {
      setFileUploadMessage('An error occurred while uploading the file. Please try again.');
    } finally {
      if (fileInput && fileInput.value) {
        fileInput.value = "";
      }
    }

    setDisableButtons(false);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedQuery = userQuery.trim();
    if (!trimmedQuery) return setSubmitMessage("Please enter your query before submitting.");

    setSubmitMessage('');
    updateConversation(prev => [...prev, { role: "User", message: trimmedQuery }]);
    setSubmitMessage('Please wait while we process your request. This may take a few seconds.');
    setDisableButtons(true);

    try {
      const response = await fetch(`${BASE_URL}/conversation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmedQuery }),
      });
      const data = await response.json();
      if (data.answer) {
        updateConversation(prev => [...prev, { role: "Bot", message: data.answer }]);
        setSubmitMessage("Response received successfully.");
      } else {
        setSubmitMessage("No response from the server.");
      }
    } catch (error) {
      setSubmitMessage('An error occurred while processing your request. Please try again.');
    } finally {
      setUserQuery("");
    }

    setDisableButtons(false);
  };

  return (
    <div className="rounded-2xl p-5 m-5 flex flex-col float-start align-middle justify-center border-slate-900 border-l-pink-900">
      <div className="text-2xl text-center">Upload a PDF to chat with it</div>
      <Separator className="bg-black mt-3 mb-3" />
      {conversation.map((conversation, index) => (
        <React.Fragment key={index}>
          <div className="flex flex-row justify-start">
            <div className="max-w-1/2">
              <img
                src={gptLogo}
                className="max-w-[30px] max-h-[30px]"
                alt=""
              />
            </div>
            <div className="max-w-1/2 pl-4">
              <span className="font-bold">{conversation.role}:</span> {conversation.message}
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
          disabled={disableButtons}
        />
      </div>
      <div className="flex flex-row items-center justify-center align-middle w-full">
        {fileUploadMessage && <p className="text-rose-600 pl-2 text-lg">{fileUploadMessage}</p>}
      </div>
      <Separator className="bg-black mt-3" />

      <form
        onSubmit={handleSubmit}
        className="flex flex-row items-center justify-center align-middle w-full"
      >
        <Textarea
          value={userQuery}
          onChange={(e) => setUserQuery(e.target.value)}
          className="w-full rounded-xl mt-5"
          placeholder="Enter your prompt here."
        />
        <Button
          variant="outline"
          type="submit"
          disabled={disableButtons}
          className="text-lg ml-4 mt-4 p-5 rounded-full"
        >
          Submit
        </Button>
      </form>

      <div className="flex flex-row items-center justify-center align-middle w-full pt-2">
        {submitMessage && <p className="text-rose-600 pl-2 text-lg">{submitMessage}</p>}
      </div>
    </div>
  );
};

export default PDFChat;
