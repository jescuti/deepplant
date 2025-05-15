import { useState, useEffect } from "react";
import { ExternalLink, ChevronLeft, X, Download } from "lucide-react";
import axios from 'axios';

export default function SearchResultsGallery({ searchData = {}, onBack }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(false);

  useEffect(() => {
    // check for results from back end  
    if (searchData?.results) {
      console.log("1000"); 
      // change backend results so they fit the UI
      const formattedResults = searchData.results.map((item, index) => {
        const catalogNumber = item.metadata?.dwc_catalog_number_ssi || "Unknown";
        const fullPlantName = item.metadata?.dwc_accepted_name_usage_ssi || item.filepath.split('/').pop().split('.')[0];
        const yearCollected = item.metadata?.dwc_year_ssi || "Unknown";
        const collectors = item.metadata?.dwc_recorded_by_ssi || "Unknown";
        const imageUrl = `data:image/jpeg;base64,${item.image}`;

        return {
          id: index + 1,
          imageUrl: imageUrl,
          title: fullPlantName,
          websiteUrl: item.websiteUrl || "https://repository.library.brown.edu/studio/collections/id_643/",
          confidence: `${(item.similarity * 100).toFixed(0)}%`,
          similarityScore: item.similarity,
          catalogNumber: catalogNumber,
          fullPlantName: fullPlantName,
          yearCollected: yearCollected,
          collectors: collectors
        };
      });
      console.log("here"); 
      console.log(searchData); 

      // const test = searchData.pdf.map((item, index) => {
      //   const pdf = item.metadata?.pdf;
      
      //   console.log("pdf", pdf); // use console.log instead of print in JavaScript
      
      //   return {
      //     pdf: pdf,
      //   };
      // });
      
      setResults(formattedResults);
      setLoading(false);

      // console.log(searchData?.pdf); 
      // console.log(searchData.results); 

      if (searchData?.pdf) {
        setPdfUrl(searchData.pdf);
      }
    } else if (searchData?.imagePreview) {
      // image but no results = fetch them from the backend
      fetchResultsFromBackend(searchData.imagePreview);
    } else {
      // no search yet
      setLoading(false);
    }
  }, [searchData]);

  // fetch results from backend using the image
  const fetchResultsFromBackend = async (imageData) => {
    setLoading(true);
    
    try {
      const base64ToBlob = (base64Data, contentType = 'image/jpeg') => {
        const byteCharacters = atob(base64Data.split(',')[1] || base64Data);
        const byteArrays = [];
      
        for (let i = 0; i < byteCharacters.length; i += 512) {
          const slice = byteCharacters.slice(i, i + 512);
          const byteNumbers = new Array(slice.length).fill().map((_, j) => slice.charCodeAt(j));
          byteArrays.push(new Uint8Array(byteNumbers));
        }
      
        return new Blob(byteArrays, { type: contentType });
      };
      
      
      const blob = base64ToBlob(imageData);
      
      const formData = new FormData();
      formData.append('image', blob, 'image.jpg');
      // num of results to fetch
      formData.append('k', '100');
      
      const response = await fetch("http://localhost:5000/api/search", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();

      console.log("Full response data:", data);


      console.log("pdf data", data.pdf); 
      
      const formattedResults = data.results.map((item, index) => {
        const catalogNumber = item.metadata?.dwc_catalog_number_ssi || "Unknown";
        const fullPlantName = item.metadata?.dwc_accepted_name_usage_ssi || item.filepath.split('/').pop().split('.')[0];
        const yearCollected = item.metadata?.dwc_year_ssi || "Unknown";
        const collectors = item.metadata?.dwc_recorded_by_ssi || "Unknown";
        
        return {
          id: index + 1,
          imageUrl: `data:image/jpeg;base64,${item.image}`,
          title: fullPlantName,
          websiteUrl: "https://repository.library.brown.edu/studio/collections/id_643/",
          confidence: `${(item.similarity * 100).toFixed(0)}%`,
          similarityScore: item.similarity,
          catalogNumber: catalogNumber,
          fullPlantName: fullPlantName,
          yearCollected: yearCollected,
          collectors: collectors
        };
      });
      
      setResults(formattedResults);

      console.log("SearchResultsGallery received searchData:", searchData);

      if (data.pdf) {
        setPdfUrl(data.pdf);
        console.log("data pdf ", data.pdf)
        // setPdfFilename(data.pdf_filename?.split('/').pop())
      }
    } catch (error) {
      console.error("Error fetching results:", error);
      // empty results if errored
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = async (base64Data, filename) => {
    if (!base64Data) {
      console.error("No PDF data available");
      return;
    }

    console.log("base 64 data", base64Data); 
  
    setDownloadLoading(true);
    try {
      const link = document.createElement('a');
      link.href = `data:application/pdf;base64,${base64Data}`;
      console.log("Download link href:", link.href);
      link.setAttribute('download', filename || "results.pdf");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      console.log("link", link); 
    } catch (error) {
      console.error("Error downloading PDF:", error);
    } finally {
      setDownloadLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div className="flex items-center">
          <button 
            onClick={onBack}
            className="flex items-center mr-4 text-customPeriwinkle hover:text-blue-800 lexend-deca"
          >
            <ChevronLeft size={20} />
            <span>Back to Search</span>
          </button>
          <h1 className="text-2xl font-bold lexend-deca text-customPeriwinkle">Similar Label Matches</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-600 lexend-deca">
            Found {results.length} matches
          </div>
          {/* {results.length > 0 && ( */}
            <button
            onClick={() => {console.log("button clicked"); downloadPdf(pdfUrl, "results.pdf")}}
            // disabled={downloadLoading || !pdfUrl}
            className={`flex items-center px-4 py-2 bg-customPeriwinkle text-white rounded-lg hover:bg-blue-700 transition-colors lexend-deca ${
              downloadLoading ? "opacity-70 cursor-not-allowed" : ""
            }`}
          >
            {downloadLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Downloading...
              </>
            ) : (
              <>
                <Download size={16} className="mr-2" />
                Download PDF
              </>
            )}
          </button>         
          {/* )} */}
        </div>
      </div>

      {/* user's inputted image */}
      {searchData?.imagePreview && (
        <div className="mb-8">
          <h2 className="text-lg font-medium mb-2 lexend-deca text-gray-700">Uploaded Image:</h2>
          <div className="inline-block rounded-lg overflow-hidden border-2 border-customPeriwinkle">
            <img 
              src={searchData.imagePreview} 
              alt="Your plant" 
              className="w-full max-w-xs h-auto object-cover"
            />
          </div>
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center h-64">
          <div className="w-16 h-16 border-4 border-customPeriwinkle border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-lg text-gray-600 lexend-deca">Identifying your plant...</p>
        </div>
      )}

      {/* gallery grid */}
      {!loading && results.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {results.map((item) => (
            <a 
            key={item.id}
            href={item.websiteUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="block bg-white rounded-lg overflow-hidden shadow-lg transition-transform hover:scale-105"
            >
            <div className="relative">
                <img 
                  src={item.imageUrl} 
                  alt={item.title} 
                  className="w-full h-48 object-cover"
                />
                <div className="absolute top-2 right-2 bg-[#6bc07d] text-white text-xs px-2 py-1 rounded-full">
                  {item.confidence}
                </div>
                <div className="absolute bottom-2 left-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
                  {item.catalogNumber}
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-bold text-lg mb-2 lexend-deca text-customPeriwinkle">{item.title}</h3>
                <div className="text-gray-600 text-sm mb-4">
                  <p><span className="font-medium">Catalog:</span> {item.catalogNumber}</p>
                  {item.yearCollected !== "Unknown" && (
                    <p><span className="font-medium">Year:</span> {item.yearCollected}</p>
                  )}
                  <p><span className="font-medium">Collector:</span> {item.collectors}</p>
                </div>
                <span 
                  // href={item.websiteUrl}
                  // target="_blank"
                  // rel="noopener noreferrer" 
                  className="flex items-center text-[#6bc07d] hover:text-green-700 font-medium lexend-deca"
                >
                  <span>Brown Digital Repository</span>
                  <ExternalLink size={16} className="ml-1" />
                </span>
              </div>
            </a>
          ))}
        </div>
      )}

      {/* no results state */}
      {!loading && results.length === 0 && searchData?.imagePreview && (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600 lexend-deca">No matching plants found.</p>
          <p className="mt-2 text-gray-500">Try uploading a clearer image or select a different label type.</p>
        </div>
      )}

      {/* no search yet */}
      {/* {!loading && !searchData?.imagePreview && (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600 lexend-deca">No search has been performed yet.</p>
          <button
            onClick={onBack}
            className="mt-4 bg-customPeriwinkle hover:bg-blue-600 text-white px-6 py-2 rounded-lg lexend-deca"
          >
            Go to Search
          </button>
        </div>
      )} */}

      {/* image detail */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-full overflow-auto">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-xl font-bold lexend-deca text-customPeriwinkle">{selectedImage.title}</h3>
              <button 
                onClick={closeImageDetail}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={24} />
              </button>
            </div>
            <div className="p-6">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="md:w-1/2">
                  <img 
                    src={selectedImage.imageUrl} 
                    alt={selectedImage.title}
                    className="w-full rounded-lg"
                  />
                </div>
                <div className="md:w-1/2">
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-500">Match Confidence</h4>
                    <p className="text-lg font-bold text-[#6bc07d]">{selectedImage.confidence}</p>
                  </div>
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-500">Similarity Score</h4>
                    <div className="mt-1 bg-gray-200 rounded-full h-4">
                    <div 
                        className="bg-[#6bc07d] h-4 rounded-full" 
                        style={{ width: `${(selectedImage.similarityScore * 100).toFixed(0)}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-500">Catalog Number</h4>
                    <p className="text-gray-700">{selectedImage.catalogNumber}</p>
                  </div>
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-500">Year Collected</h4>
                    <p className="text-gray-700">{selectedImage.yearCollected}</p>
                  </div>
                  <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-500">Collectors</h4>
                    <p className="text-gray-700">{selectedImage.collectors}</p>
                  </div>
                  <a 
                    href={selectedImage.websiteUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-[#6bc07d] hover:text-green-700 font-medium lexend-deca"
                  >
                    View in Brown Digital Repository
                    <ExternalLink size={16} className="ml-2" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
