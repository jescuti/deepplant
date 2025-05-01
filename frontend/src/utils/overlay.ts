import { FeatureCollection } from "geojson";
import { FillLayer } from "react-map-gl";
import { getGeoData } from "./api";

const propertyName = "holc_grade";
export const geoLayer: FillLayer = {
  id: "geo_data",
  type: "fill",
  paint: {
    "fill-color": [
      "match",
      ["get", propertyName],
      "A",
      "#5bcc04",
      "B",
      "#04b8cc",
      "C",
      "#e9ed0e",
      "D",
      "#d11d1d",
      "#ccc",
    ],
    "fill-opacity": 0.2,
  },
  source: ""
};


// TODO: MAPS PART 4:
// - Download and import the geojson file
// - Implement the two functions below.

// Import the raw JSON file
// import rl_data from "../geodata/fullDownload.json";
// you may need to rename the downloaded .geojson to .json

function isFeatureCollection(json: any): json is FeatureCollection {
  return json.type === "FeatureCollection";
}

let response: { result: string; data: FeatureCollection };
let rl_data: any;

export async function overlayData(
  input: string
): Promise<GeoJSON.FeatureCollection | undefined> {
  response = await getGeoData(input);
  rl_data = response["data"];
  return isFeatureCollection(rl_data) ? rl_data : undefined;
}

// export function overlayData(): GeoJSON.FeatureCollection | undefined {
//   return isFeatureCollection(rl_data) ? rl_data : undefined;
// }
