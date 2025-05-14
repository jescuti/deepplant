import { useState, useEffect } from "react";
import { ExternalLink, ChevronLeft, X } from "lucide-react";

export default function SearchResultsGallery({ searchData = {}, onBack }) {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);

  // get label type from searchData
  // const labelType = searchData?.labelType || "unknown";

  useEffect(() => {
    // check for results from back end  
    if (searchData?.results) {
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
      
      setResults(formattedResults);
      setLoading(false);
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
      const base64Response = await fetch(imageData);
      const blob = await base64Response.blob();
      
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
          description: `Similar plant based on visual features`,
          similarityScore: item.similarity,
          catalogNumber: catalogNumber,
          fullPlantName: fullPlantName,
          yearCollected: yearCollected,
          collectors: collectors
        };
      });
      
      setResults(formattedResults);
    } catch (error) {
      console.error("Error fetching results:", error);
      // empty results if errored
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const openImageDetail = (image) => {
    setSelectedImage(image);
  };

  const closeImageDetail = () => {
    setSelectedImage(null);
  };

  const extractBdrId = (url) => {
    const match = url.match(/bdr:([^/]+)/);
    return match ? match[1] : null;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* header */}
      <div className="flex justify-between items-center mb-8">
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
        <div className="text-sm text-gray-600 lexend-deca">
          Found {results.length} matches
        </div>
      </div>

      {/* user's inputted image */}
      {searchData?.imagePreview && (
        <div className="mb-8">
          <h2 className="text-lg font-medium mb-2 lexend-deca text-gray-700">Your Plant Image:</h2>
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
            <div 
              key={item.id} 
              className="bg-white rounded-lg overflow-hidden shadow-lg transition-transform hover:scale-105"
            >
              <div 
                className="relative cursor-pointer"
                onClick={() => openImageDetail(item)}
              >
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
                </div>
                <a 
                  href={item.websiteUrl}
                  target="_blank"
                  rel="noopener noreferrer" 
                  className="flex items-center text-[#6bc07d] hover:text-green-700 font-medium lexend-deca"
                >
                  <span>Brown Digital Repository</span>
                  <ExternalLink size={16} className="ml-1" />
                </a>
              </div>
            </div>
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
      {!loading && !searchData?.imagePreview && (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600 lexend-deca">No search has been performed yet.</p>
          <button
            onClick={onBack}
            className="mt-4 bg-customPeriwinkle hover:bg-blue-600 text-white px-6 py-2 rounded-lg lexend-deca"
          >
            Go to Search
          </button>
        </div>
      )}

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
