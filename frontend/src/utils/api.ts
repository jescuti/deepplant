import { LatLong } from "../components/Mapbox";

const HOST = "http://localhost:3232";

async function queryAPI(
  endpoint: string,
  query_params: Record<string, string>
) {
  // query_params is a dictionary of key-value pairs that gets added to the URL as query parameters
  // e.g. { foo: "bar", hell: "o" } becomes "?foo=bar&hell=o"
  const paramsString = new URLSearchParams(query_params).toString();
  const url = `${HOST}/${endpoint}?${paramsString}`;
  const response = await fetch(url);
  if (!response.ok) {
    console.error(response.status, response.statusText);
  }
  return response.json();
}

export async function addWord(uid: string, word: string) {
  return await queryAPI("add-word", {
    uid: uid,
    word: word,
  });
}

export async function getWords(uid: string) {
  return await queryAPI("list-words", {
    uid: uid,
  });
}

// add a pin to firebase data
export async function addPin(uid: string, loc: LatLong) {
  return await queryAPI("add-pin", {
    uid: uid,
    lat: loc.lat.toString(),
    long: loc.long.toString(),
  });
}

// request all user pins from firebase
export async function getPins(uid: string) {
  return await queryAPI("get-pins", {
    uid: uid,
  });
}

export async function clearUser(uid: string) {
  return await queryAPI("clear-user", {
    uid: uid,
  });
}

// request all all Geo Data from api
export async function getGeoData(keyword: string) {
  return await queryAPI("data-request", {
    keyword: keyword || "",
  });
}



// add endpoints
