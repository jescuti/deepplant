import { useState, useEffect } from "react";
import { ExternalLink, ChevronLeft, X } from "lucide-react";
import aloeVera from '../assets/397772_1.jpg';
import peaceLily from '../assets/397772_14.jpg'; 
import spiderPlant from '../assets/699845_14.jpg'; 
import olney2 from '../assets/olney5.jpg';
import olney3 from '../assets/olney2.jpg';
import olney4 from '../assets/olney3.jpg';
import olney5 from '../assets/olney4.jpg';

export default function SearchResultsGallery({ searchData = {}, onBack }) {
  // Mock data for search results
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(null);

  // Get label type from searchData
  const labelType = searchData?.labelType || "unknown";

  // Simulate loading results from API
  useEffect(() => {
    // Mock delay to simulate API call
    const timer = setTimeout(() => {
      // Generate different results based on label type
      if (labelType === "machine-label") {
        setResults([
          {
            id: 1,
            imageUrl: "/Users/ashleywoertz/Desktop/CSCI1430_Projects/deepplant/frontend/src/assets/397772_1.jpg",
            title: "Monstera Deliciosa",
            websiteUrl: "https://example.com/plants/monstera",
            confidence: "98%",
            description: "Popular tropical houseplant with large, split leaves"
          },
          {
            id: 2,
            imageUrl: "/api/placeholder/400/320",
            title: "Fiddle Leaf Fig",
            websiteUrl: "https://example.com/plants/fiddle-leaf",
            confidence: "95%",
            description: "Trendy indoor plant with violin-shaped leaves"
          },
          {
            id: 3,
            imageUrl: "/api/placeholder/400/320",
            title: "Snake Plant",
            websiteUrl: "https://example.com/plants/snake-plant",
            confidence: "93%",
            description: "Low-maintenance succulent with tall, stiff leaves"
          },
          {
            id: 4,
            imageUrl: "/api/placeholder/400/320",
            title: "Pothos",
            websiteUrl: "https://example.com/plants/pothos",
            confidence: "91%",
            description: "Popular trailing vine with heart-shaped leaves"
          }
        ]);
      } else if (labelType === "handwriting") {
        setResults([
          {
            id: 1,
            imageUrl: aloeVera,
            title: "Aloe Vera",
            websiteUrl: "https://example.com/plants/aloe",
            confidence: "94%",
            description: ""
          },
          {
            id: 2,
            imageUrl: peaceLily,
            title: "Peace Lily",
            websiteUrl: "https://example.com/plants/peace-lily",
            confidence: "90%",
            description: ""
          },
          {
            id: 3,
            imageUrl: spiderPlant,
            title: "Spider Plant",
            websiteUrl: "https://example.com/plants/spider-plant",
            confidence: "88%",
            description: ""
          }
        ]);
      } else {
        // Default results
        setResults([
          {
            id: 1,
            imageUrl: olney2,
            title: "Planispicata",
            websiteUrl: "https://example.com/plants/zz-plant",
            confidence: "89%",
            description: ""
          },
          {
            id: 2,
            imageUrl: olney3,
            title: "Calathea",
            websiteUrl: "https://example.com/plants/calathea",
            confidence: "87%",
            description: ""
          },
          {
            id: 3,
            imageUrl: olney4,
            title: "Carex",
            websiteUrl: "https://example.com/plants/calathea",
            confidence: "87%",
            description: ""
          },
          {
            id: 4,
            imageUrl: olney5,
            title: "Debilis",
            websiteUrl: "https://example.com/plants/calathea",
            confidence: "87%",
            description: ""
          }
        ]);
      }
      setLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, [labelType]);

  // Function to open image detail modal
  const openImageDetail = (image) => {
    setSelectedImage(image);
  };

  // Function to close image detail modal
  const closeImageDetail = () => {
    setSelectedImage(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center">
          <button 
            onClick={onBack}
            className="flex items-center mr-4 text-customPeriwinkle hover:text-blue-800 lexend-deca"
          >
            <ChevronLeft size={20} />
            <span>Back to Search</span>
          </button>
          <h1 className="text-2xl font-bold lexend-deca text-customPeriwinkle">Plant Matches</h1>
        </div>
        <div className="text-sm text-gray-600 lexend-deca">
          Found {results.length} matches
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="flex flex-col items-center justify-center h-64">
          <div className="w-16 h-16 border-4 border-customPeriwinkle border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-lg text-gray-600 lexend-deca">Identifying your plant...</p>
        </div>
      )}

      {/* Gallery grid */}
      {!loading && (
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
              </div>
              <div className="p-4">
                <h3 className="font-bold text-lg mb-2 lexend-deca text-customPeriwinkle">{item.title}</h3>
                <p className="text-gray-600 text-sm mb-4">{item.description}</p>
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

      {/* No results state */}
      {!loading && results.length === 0 && (
        <div className="text-center py-12">
          <p className="text-xl text-gray-600 lexend-deca">No matching plants found.</p>
          <p className="mt-2 text-gray-500">Try uploading a clearer image or selecting a different label type.</p>
        </div>
      )}

      {/* Image detail modal */}
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
                    <h4 className="text-sm font-medium text-gray-500">Description</h4>
                    <p className="text-gray-800">{selectedImage.description}</p>
                  </div>
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-500">Care Tips</h4>
                    <ul className="list-disc pl-5 text-gray-700 mt-2">
                      <li>Water: {selectedImage.id % 2 === 0 ? "Keep soil slightly moist" : "Allow to dry between waterings"}</li>
                      <li>Light: {selectedImage.id % 3 === 0 ? "Bright indirect light" : "Medium to low light"}</li>
                      <li>Humidity: {selectedImage.id % 2 === 0 ? "High" : "Average"}</li>
                    </ul>
                  </div>
                  <a 
                    href={selectedImage.websiteUrl}
                    target="_blank"
                    rel="noopener noreferrer" 
                    className="inline-flex items-center px-4 py-2 bg-[#6bc07d] text-white rounded hover:bg-green-600 lexend-deca"
                  >
                    <span>Learn More</span>
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