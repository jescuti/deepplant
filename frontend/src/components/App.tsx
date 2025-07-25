import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import "../styles/App.css";
import "../styles/index.css";
import "../output.css";
import Footer from "./Footer";
import PottedPlant from "../assets/PottedPlant.png";
import { SignedIn, SignedOut, SignInButton, SignOutButton, SignUpButton, UserButton, UserProfile } from "@clerk/clerk-react";
import SearchInitiation from "./SearchInitiation";
import SearchResultsGallery from "./SearchResultsGallery";
import { useState } from "react";

function SearchInitiationWithNavigation() {
  const navigate = useNavigate();
  const [searchData, setSearchData] = useState(null);

  const handleSearchSubmit = (data) => {
    // store search data in localStorage to persist between routes
    localStorage.setItem('searchData', JSON.stringify(data));
    // navigate to results page
    navigate('/search-results');
  };

  return <SearchInitiation onSubmitComplete={handleSearchSubmit} />;
}

// handle navigation
function SearchResultsWithNavigation() {
  const navigate = useNavigate();
  // get search data from localStorage
  const searchData = JSON.parse(localStorage.getItem('searchData') || '{}');

  const handleBackToSearch = () => {
    navigate('/search-initiation');
  };

  return <SearchResultsGallery searchData={searchData} onBack={handleBackToSearch} />;
}

function App() {
  return (
    <Router>
      <div className="bg-customMint min-h-screen flex flex-col">
        <SignedIn>
          <div className="flex flex-row justify-between items-center p-4 mt-4">
            <div className="basis-1/4"></div>
            <div className="basis-1/2 flex flex-row items-center justify-center">
              <img
                src={PottedPlant}
                alt="A potted plant"
                className="w-12 md:w-32 h-auto overflow-hidden relative"
              />
              <p
                className="lexend-deca text-2xl md:text-5xl xl:text-7xl text-customPeriwinkle"
                aria-label="Page Title"
              >
                DeepPlant
              </p>
            </div>
            <div className="flex justify-end basis-1/4">
              <div className="flex items-center justify-center mx-4 my-auto">
                <UserButton />
              </div>
              <div className="lexend-deca bg-[#6bc07d] text-white rounded-lg flex items-center justify-center text-md w-24 md:w-28 h-8 md:h-11 md:text-xl">
                <SignOutButton>LOG OUT</SignOutButton>
              </div>
            </div>
          </div>
        </SignedIn>

        <main className="flex-grow flex flex-col">
          <SignedIn>
            <div className="flex-grow">
              <Routes>
                <Route path="/" element={<SearchInitiationWithNavigation />} />
                <Route path="/search-initiation" element={<SearchInitiationWithNavigation />} />
                <Route path="/search-results" element={<SearchResultsWithNavigation />} />
                <Route path="/profile" element={<UserProfile />} />
              </Routes>
            </div>
          </SignedIn>

          <SignedOut>
            <div className="flex flex-col items-center justify-center flex-grow my-auto">
              <img
                src={PottedPlant}
                alt="A potted plant"
                className="w-64 md:w-96 h-auto overflow-hidden relative"
              />
              <p
                className="lexend-deca text-3xl md:text-7xl text-center text-customPeriwinkle mb-10"
                aria-label="Page Title"
              >
                DeepPlant
              </p>
              <div className="flex justify-center flex-row space-x-3 md:space-x-7">
                <div className="lexend-deca bg-[#6bc07d] text-white rounded-lg text-md px-3 py-1 md:px-7 md:py-2 md:text-xl">
                  <SignUpButton>SIGN UP</SignUpButton>
                </div>
                <div className="lexend-deca bg-[#6bc07d] text-white rounded-lg text-md px-3 py-1 md:px-7 md:py-2 md:text-xl">
                  <SignInButton>LOG IN</SignInButton>
                </div>
              </div>
            </div>
          </SignedOut>
        </main>
        
        <Footer />
      </div>
    </Router>
  );
}

export default App;