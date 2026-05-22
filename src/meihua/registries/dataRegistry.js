import hexagramData from "../data/hexagram_wuxing.json" assert { type: "json" };

class DataRegistry {
  constructor() { this.hexagrams = hexagramData; }
  getHexagram(name) { return this.hexagrams[name] ?? null; }
  getAllHexagrams() { return this.hexagrams; }
}

export default new DataRegistry();
