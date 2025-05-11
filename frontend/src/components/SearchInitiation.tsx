import { useState, useEffect, useRef } from "react";
import { Camera, X } from "lucide-react";
import Webcam from "react-webcam";

export default function SearchInitiation({ onSubmitComplete }) {
  const variableRef = useRef(null);
  const [variableSelection, selectVariable] = useState('');
  const [image, setImage] = useState(null);
  const [showCamera, setShowCamera] = useState(false);
  const fileInputRef = useRef(null);
  const webcamRef = useRef(null);
  const [loading, setLoading] = useState(false);

  // text input
  const [inputTextMode, setInputTextMode] = useState(false);
  const [inputText, setInputText] = useState('');


  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setImage(event.target.result);
        setShowCamera(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const openCamera = () => {
    setShowCamera(true);
  };

  const closeCamera = () => {
    setShowCamera(false);
  };

  const capturePhoto = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImage(imageSrc);
    setShowCamera(false);
  };

  const handleSubmit = () => {
    if (!variableSelection && !inputTextMode) {
      alert("Please select a label type");
      return;
    }
    
    if (!image && !inputText.trim()) {
      alert("Please upload, capture an image, or enter text.");
      return;
    }
    
    if (!image && !inputText.trim()) {
      alert("Please upload, capture an image, or enter text.");
      return;
    }
    
    const submission = {
      labelType: variableSelection,
      imageData: image ? image.substring(0, 100) + "..." : null,
      textData: inputTextMode ? inputText.trim() : null
    };
    
    setLoading(true);
    
    // Simulate API call with setTimeout
    setTimeout(() => {
      console.log("Submitting:", {
        labelType: variableSelection,
        imageData: image ? image.substring(0, 100) + "..." : null,
        textData: inputTextMode ? inputText.trim() : null
      });      
      
      setLoading(false);
      
      // If onSubmitComplete callback is provided, call it
      // This allows the parent component to handle navigation
      if (onSubmitComplete && typeof onSubmitComplete === 'function') {
        onSubmitComplete({
          labelType: variableSelection,
          imagePreview: image,
          text: inputText.trim()
        });        
      } else {
        alert("Image submitted successfully!");
      }
    }, 1000);
  };

  return (
    <div className="space-y-10">
      <div className="flex flex-col items-center justify-center mt-8 lg:mt-12 space-y-6">
        <select
          className="px-4 py-2 m-0 h-auto leading-none text-base border border-black rounded max-w-full min-w-[150px] sm:min-w-[200px] sm:max-w-[400px] align-bottom"
          name="variable-dropdown"
          id="variable-dropdown"
          aria-label="variable-dropdown"
          onChange={(e) => selectVariable(e.target.value)}
          value={variableSelection}
          ref={variableRef}
          aria-describedby="variable-description"
        >
          <option value="">Select Label Type</option>
          <option value="machine-label">Machine Printed Label</option>
          <option value="handwriting">Handwritten Label</option>
        </select>

        {!showCamera && (
          <div className="flex flex-row space-x-4">
            <button
              onClick={triggerFileInput}
              className="bg-customPeriwinkle lexend-deca hover:bg-blue-600 text-white px-4 py-2 rounded flex items-center"
            >
              <span className="mr-2">Upload Image</span>
            </button>
            
            <button
              onClick={openCamera}
              className="bg-[#6bc07d] lexend-deca hover:bg-green-600 text-white px-4 py-2 rounded flex items-center"
            >
              <Camera size={20} className="mr-2" />
              <span>Take Photo</span>
            </button>

            <button
              onClick={() => {
                setInputTextMode(true);
                setImage(null);
              }}
              className="bg-[#00bd9d] lexend-deca hover:bg-green-600 text-white px-4 py-2 rounded flex items-center"
            >
              <span>Input Text String</span>
            </button>
            
            <input
              type="file"
              accept="image/*"
              className="hidden"
              ref={fileInputRef}
              onChange={handleFileSelect}
            />
          </div>
        )}

        {showCamera && (
          <div className="relative">
            <button 
              onClick={closeCamera}
              className="absolute top-2 right-2 z-10 bg-customPeriwinkle text-white p-1 rounded-full"
            >
              <X size={24} />
            </button>
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              className="w-full max-w-md rounded border border-gray-300"
            />
            <button
              onClick={capturePhoto}
              className="mt-4 bg-[#6bc07d] hover:bg-green-600 text-white px-4 py-2 rounded w-full"
            >
              Capture Photo
            </button>
          </div>
        )}

        {image && !showCamera && (
          <div className="mt-4">
            <img
              src={image}
              alt="Selected"
              className="max-w-xs max-h-64 rounded border border-gray-300"
            />
          </div>
        )}
        
        {image && !showCamera && (
          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`bg-[#6bc07d] hover:bg-green-600 text-white px-6 py-3 rounded-lg font-semibold text-lg transition-all ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {loading ? 'Submitting...' : 'Submit Image'}
          </button>
        )}

        {inputTextMode && (
          <div className="w-full max-w-md mt-4">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter text here..."
              className="w-full p-3 border border-gray-300 rounded"
              rows={4}
            />
          </div>
        )}

        {(image || (inputTextMode && inputText.trim())) && !showCamera && (
          <button
            onClick={handleSubmit}
            disabled={loading}
            className={`bg-[#6bc07d] hover:bg-green-600 text-white px-6 py-3 rounded-lg font-semibold text-lg transition-all ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            {loading ? 'Submitting...' : 'Submit'}
          </button>
        )}

      </div>
    </div>
  );
}