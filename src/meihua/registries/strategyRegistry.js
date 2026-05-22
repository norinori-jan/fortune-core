class StrategyRegistry {
  constructor() { this.strategies = new Map(); }
  register(name, strategy) { this.strategies.set(name, strategy); }
  get(name) { return this.strategies.get(name) ?? null; }
}

export default new StrategyRegistry();
